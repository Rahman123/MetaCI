import time
from collections import namedtuple

import django_rq
from django import db
from django.conf import settings
from django.core.cache import cache
from rq.exceptions import ShutDownImminentException

from metaci.build.autoscaling import autoscale
from metaci.build.exceptions import RequeueJob
from metaci.build.signals import build_complete
from metaci.cumulusci.models import Org, jwt_session, sf_session
from metaci.repository.utils import create_status

ACTIVESCRATCHORGLIMITS_KEY = "metaci:activescratchorgs:limits"

ActiveScratchOrgLimits = namedtuple("ActiveScratchOrgLimits", ["remaining", "max"])


def reset_database_connection():
    db.connection.close()


def scratch_org_limits():
    cached = cache.get(ACTIVESCRATCHORGLIMITS_KEY, None)
    if cached:
        return cached

    sfjwt = jwt_session(username=settings.SFDX_HUB_USERNAME)
    limits = sf_session(sfjwt).limits()["ActiveScratchOrgs"]
    value = ActiveScratchOrgLimits(remaining=limits["Remaining"], max=limits["Max"])
    # store it for 65 seconds, enough til the next tick. we may want to tune this
    cache.set(ACTIVESCRATCHORGLIMITS_KEY, value, 65)
    return value


def run_build(build_id, lock_id=None):
    reset_database_connection()
    from metaci.build.models import Build

    try:
        build = Build.objects.get(id=build_id)
    except Build.DoesNotExist:
        time.sleep(1)
        build = Build.objects.get(id=build_id)

    try:
        build.run()
        if settings.GITHUB_STATUS_UPDATES_ENABLED:
            res_status = set_github_status.delay(build_id)
            build.task_id_status_end = res_status.id

        build.save()

        build_complete.send(
            sender=build.__class__, build=build, status=build.get_status()
        )

    except ShutDownImminentException:
        # The Heroku dyno is restarting.
        # Log that, leave the build's status as running,
        # and let the exception fall through to the rq worker to requeue the job.
        build.log += (
            "\nERROR: Build aborted because the Heroku dyno restarted. "
            "MetaCI will try to start a rebuild."
        )
        build.save()
        raise RequeueJob
    except Exception as e:
        if lock_id:
            cache.delete(lock_id)
        if settings.GITHUB_STATUS_UPDATES_ENABLED:
            res_status = set_github_status.delay(build_id)
            build.task_id_status_end = res_status.id

        build.set_status("error")
        build.log += "\nERROR: The build raised an exception\n"
        build.log += str(e)
        build.save()

        build_complete.send(
            sender=build.__class__, build=build, status=build.get_status()
        )

    if lock_id:
        cache.delete(lock_id)

    return build.get_status()


def start_build(build, lock_id=None):
    queue = django_rq.get_queue(build.plan.queue)
    result = queue.enqueue(
        run_build, build.id, lock_id, job_timeout=build.plan.build_timeout
    )
    build.task_id_check = None
    build.task_id_run = result.id
    build.save()
    autoscale()
    return result


def lock_org(org, build_id, timeout):
    return cache.add(org.lock_id, f"build-{build_id}", timeout=timeout)


@django_rq.job("short", timeout=60)
def check_queued_build(build_id):
    reset_database_connection()

    from metaci.build.models import Build

    try:
        build = Build.objects.get(id=build_id)
    except Build.DoesNotExist:
        time.sleep(1)
        build = Build.objects.get(id=build_id)

    # Check for concurrency blocking
    try:
        org = build.org or Org.objects.get(name=build.plan.org, repo=build.repo)
    except Org.DoesNotExist:
        message = "Could not find org configuration for org {}".format(build.plan.org)
        build.log = message
        build.set_status("error")
        build.save()
        return message

    if org.scratch:
        # For scratch orgs, we don't need concurrency blocking logic,
        # but we need to check capacity

        if scratch_org_limits().remaining < settings.SCRATCH_ORG_RESERVE:
            build.task_id_check = None
            build.set_status("waiting")
            msg = "DevHub does not have enough capacity to start this build. Requeueing task."
            build.log = msg
            build.save()
            return msg
        res_run = start_build(build)
        return (
            "DevHub has scratch org capacity, running the build "
            + "as task {}".format(res_run.id)
        )
    else:
        # For persistent orgs, use the cache to lock the org
        status = lock_org(org, build_id, build.plan.build_timeout)

        if status is True:
            # Lock successful, run the build
            res_run = start_build(build, org.lock_id)
            return "Got a lock on the org, running as task {}".format(res_run.id)
        else:
            # Failed to get lock, queue next check
            build.task_id_check = None
            build.set_status("waiting")
            build.log = "Waiting on build #{} to complete".format(
                cache.get(org.lock_id)
            )
            build.save()
            return (
                "Failed to get lock on org. "
                + "{} has the org locked. Queueing next check.".format(
                    cache.get(org.lock_id)
                )
            )


@django_rq.job("short", timeout=60)
def check_waiting_builds():
    reset_database_connection()

    from metaci.build.models import Build

    builds = []
    for build in Build.objects.filter(status="waiting").order_by("time_queue"):
        builds.append(build.id)
        res_check = check_queued_build.delay(build.id)
        build.task_id_check = res_check.id
        build.save()

    if builds:
        return "Checked waiting builds: {}".format(builds)
    else:
        return "No queued builds to check"


@django_rq.job("short")
def set_github_status(build_id):
    reset_database_connection()

    from metaci.build.models import Build

    build = Build.objects.get(id=build_id)
    create_status(build)


@django_rq.job("short")
def delete_scratch_orgs():
    reset_database_connection()

    from metaci.cumulusci.models import ScratchOrgInstance

    count = 0
    for org in ScratchOrgInstance.objects.filter(
        deleted=False, delete_error__isnull=False
    ):
        delete_scratch_org.delay(org.id)
        count += 1

    if not count:
        return "No orgs found to delete"

    return "Scheduled deletion attempts for {} orgs".format(count)


@django_rq.job("short")
def delete_scratch_org(org_instance_id):
    reset_database_connection()
    from metaci.cumulusci.models import ScratchOrgInstance

    try:
        org = ScratchOrgInstance.objects.get(id=org_instance_id)
    except ScratchOrgInstance.DoesNotExist:
        return "Failed: could not find ScratchOrgInstance with id {}".format(
            org_instance_id
        )

    org.delete_org()
    if org.deleted:
        return "Deleted org instance #{}".format(org.id)
    else:
        return "Failed to delete org instance #{}".format(org.id)
