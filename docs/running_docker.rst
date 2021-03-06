========================
Docker Development Setup
========================

Cloning the project
-------------------

::

    git clone git@github.com:SFDO-Tooling/MetaCI
    cd MetaCI

Docker and Docker-Compose Installation
--------------------------------------

To download and install docker please visit: https://hub.docker.com/?overlay=onboarding 
and follow the installation instructions to download docker if needed.
To verify you have successfully installed docker type:

::
    
    docker -v

*You should see something like the following:*
    ``Docker version 19.03.4, build 9013bf5``


To download and install docker-compose please visit: https://docs.docker.com/v17.09/compose/install/
and follow the installation instructions to download docker-compose if needed.
To verify you have successfully installed docker-compose type:

::

    docker-compose -v

*You should see something like the following:*
    ``docker-compose version 1.16.1, build 6d1ac219``

Running MetaCI In Docker
========================

Below are the following steps necessary to run MetaCI on Docker:

1. `.env File Creation and Variable Declaration`_
    __ `.env File Creation and Variable Declaration`

2. `Building Your Docker Containers`_ 
    __ `Building Your Docker Containers`


3. `Running Your Docker Containers`_
    __ `Running Your Docker Containers`


.env File Creation And Variable Declaration
-------------------------------------------

*Please begin by making a copy of env.example and renaming it .env in your root project directory*

Local Variables
---------------

POSTGRES_USER:
    Environment variable set in ``.env``, representing the database username.
    This value defaults to ``metaci``.

POSTGRES_PASSWORD: 
    Environment variable set in ``.env``, representing the database password.
    This value defaults to ``metaci``.

POSTGRES_DB:
    Environment variable set in ``.env``, representing the database name.
    This value defaults to ``metaci``.

MetaCI must authenticate with the GitHub API to fetch repositories and create releases. 
This can be set up for a GitHub user by setting GITHUB_USERNAME and GITHUB_PASSWORD, 
or for a GitHub App by setting GITHUB_APP_ID and GITHUB_APP_KEY.

GITHUB_USERNAME:     
    This represents the username of either the tester or service account configured for MetaCI

GITHUB_PASSWORD:      
    This represents the password or personal access token a user must have to access 
    their account a `personal access token` will be used when Multi Factor Authentication is enabled.

OR

GITHUB_APP_ID:
    This represents the app id of your github app allowing you to authenticate your machine
    with github.

GITHUB_APP_KEY:
    This represents the private key used for authentication for github applications.

If you need to generate a personal access token please visit `Github's documentation`_:

.. _Github's documentation: https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line

SFDX_CLIENT_ID:       
    This tells sfdx the client id of the connected app to use for connecting to 
    the Dev Hub to create scratch orgs (so it's only needed for running plans that use a scratch org).
    If you are a member of SFDO please reach out to Release Engineering for help acquiring the proper SFDX_CLIENT_ID. 
    For SFDO release engineering staff it's easiest to use an existing connected app, so its best to ask another team member. 
    External users setting up MetaCI will need to create their own connected app, 
    which they can do in the Dev Hub org. 
    You can adapt these instructions https://cumulusci.readthedocs.io/en/latest/tutorial.html#creating-manually 
    but there is a difference for MetaCI: because it's connecting to the org non-interactively, 
    the connected app needs to be set up to use the JWT oauth flow. 
    That means when creating the connected app the user needs to check the "Use Digital Signatures" 
    box and upload a certificate. 

SFDX_HUB_KEY:          
    SFDX_HUB_KEY is the private key that was used to create the certificate.
    Shared through last pass. In the form of a pem key. 
    Called `SFDX Hub Org Key` n Release Engineering folder.
    
FORMATTING SFDX_HUB_KEY in .env
    IMPORTANT to format on a single line, escaping each newline in the key with ``\n``
    character otherwise the variable will not be read correctly. Must look like the 
    following example and CANNOT BE IN QUOTES:

::

    SFDX_HUB_KEY=-----BEGIN RSA PRIVATE KEY-----\nMINDSJIBAAAFDVCXwVAe1YBRi+WpkTp02mOPbgj9NgjpwKQEOJugAqdzBdprBxTs\nMINDSJIBAAAFDVCXwVAe1YBRi+WpkTp02mOPbgj9NgjpwKQEOJugAqdzBdprBxTs\nMINDSJIBAAAFDVCXwVAe1YBRi+WpkTp02mOPbgj9NgjpwKQEOJugAqdzBdprBxTs\nv4fU8l7TeYVQVvSdWJmN3sBZ4bnG3GSu1u6viGQwxulxtJrLnclEgL2Tq0npRn/x\nMINDSJIBAAAFDVCXwVAe1YBRi+WpkTp02mOPbgj9NgjpwKQEOJugAqdzBdprBxTs\nMINDSJIBAAAFDVCXwVAe1YBRi+WpkTp02mOPbgj9NgjpwKQEOJugAqdzBdprBxTs\nMINDSJIBAAAFDVCXwVAe1YBRi+WpkTp02mOPbgj9NgjpwKQEOJugAqdzBdprBxTs\nDMG9uoYPD4X0rkKz/4PI2jcO4NgkWfTiQY0yEDQNM31Sfcw5lNSeKHrrnG7fHx3q\nu9fb7GxWMi74LBlMVlseREzfYRyUI7ukPZNgdvAGbp3TI0ITAQTbTzKPR4FdyZbm\nysuDXZuQpbifXxBKPVVYHxbdEYkabK4FKeB1cNRI72T0jt+r6DqFTjfpJHs/FjEo\nq86HWtHWGh1AYaIi5LBMLQ1tNEcSNvvZW49AsUISqJRFwFvwubBhLh36DaucM4aI\nWPLQUeUCgYEA37+Qy6o3vvfwj0pJ4Ecqo5FRZkxBbUmVTdr1RVPAFxRchsKzsvx4\nWKRDkmIlvf/vpaB4cUsYDZVOd1qGXciFQODk+FfLbOCDbcR1qv87YL/tKNRO/sox\nBt3yS6vyCokn48Ycaqs+tYcHC2O0Vaye/VvwwUSQMLLVdGR84N2hzX8CgYEA3S15\ndqEiWI8a27EX4AD4q9avNJJCwkO5B9/YBnZBpy1DcFSozP5JfgoH1ilK4tmiXjZO\n3Y+oTcKRUKOSQPjv8obTt3N3xtdabWMW6sH31kOfiKOmDg2lw/UjYQ+xO5FBE/Pi\nOR4XRbhSe04dJ+U2Gik38f/WtgA9h53YOeAJ5UMCgYA2kFLRN+tsSK6DYwxtAy3k\nwZVmKwZxjlY4rELP60KW3kJKIsULywHWLAjGc+TcVsOsUlvM1RFCjryZ4puN106X\nMINDSJIBAAAFDVCXwVAe1YBRi+WpkTp02mOPbgj9NgjpwKQEOJugAqdzBdprBxTs\nMINDSJIBAAAFDVCXwVAe1YBRi+WpkTp02mOPbgj9NgjpwKQEOJugAqdzBdprBxTs\nMINDSJIBAAAFDVCXwVAe1YBRi+WpkTp02mOPbgj9NgjpwKQEOJugAqdzBdprBxTs\nDtfenYxFW9Iqj58oCzDuUJGWkA4lolYMkcbvEhE2fhOTNH9UdFyhC6WDQuaFnr1x\nbC4LAoGAbzqfS4vF+kloxneGdWJnAiibvEEUWVmMZ4GMF0a7w0x2l+jwiGT2Kt8P\nC5VdZvMMktzfTHynq6j6BfnSYCBJFNp1EbwZksGtEnT4ggCdIVNY+N1wVeok1vp/\n17/R87a1O62MeA5gBeGdpoMof/XrFVUdb/kSXyNt8miUeLOez/M=\n-----END RSA PRIVATE KEY-----

SFDX_HUB_USERNAME: 
    This represents the username used to login to your sfdx hub account

CONNECTED_APP_CLIENT_ID:
    This represents the client id of the connected app that MetaCI will use for authenticating to any persistent org. 
    It's fine to use the same connected app that is being used for SFDX_CLIENT_ID and SFDX_HUB_KEY.

CONNECTED_APP_CLIENT_SECRET: 
    This represents the secret of the packaging org configured for MetaCI

CONNECTED_APP_CALLBACK_URL:
    This represents the packaging org's callback url 

To acquire the connected_app variables just use the client id, client secret and callback url 
of the connected app that was created for ``SFDX_CLIENT_ID`` and ``SFDX_HUB_KEY``.


Production Variables
--------------------

GITHUB_WEBHOOK_SECRET
    definition here
DJANGO_AWS_ACCESS_KEY_ID
    definition here
DJANGO_AWS_SECRET_ACCESS_KEY
    definition here
DJANGO_AWS_STORAGE_BUCKET_NAME
    definition here
DJANGO_SERVER_EMAIL
    definition here
DJANGO_SENTRY_DSN
    definition here


Other Variables 
---------------

*Some variables are preset in this section if this is the case it will explicitly tell you where its declaration is in the description.*

DJANGO_SECRET_KEY: 
    This represents the secret key for the django web application and is used to sign session cookies;, 
    arbritary strings such as the one given in the env.example are used. Important this variable is 
    not copied from another Django site.

CHROMEDRIVER_DIR:
    This environment variable represents the directory where the chromedriver package resides
    in the filesystem. CHROMEDRIVER_DIR is set for you in the Dockerfile.

NODE_VERSION: 
    Environment variable used to set node version for download, this variable is set in the Dockerfile

YARN_VERSION: 
    Environment variable used to set yarn version for download, this variable is set in the Dockerfile

PYTHONUNBUFFERED: 
    Environment variable set in Dockerfile used to not write .pyc files to Docker container
       
DATABASE_URL:
    Environment variable set in Dockerfile. Represents the full path of database url.

REDIS_URL: 
    This represents the url to the location where the redis server, configured for Meta CI. Set in Dockerfile.

DJANGO_HASHID_SALT: 
    This represents the hashid salt for the django application, currently set to 
    arbritary string due to non production defaults, can be overridden 
    in docker-compose.yml. Currently set in Dockerfile.

DJANGO_SECRET_KEY: 
    This represents the key for the django web application, currently set to arbritary
    string due to non production defaults, can be overridden in docker-compose.yml.
    Currently set in Dockerfile. For local testing, arbritary strings such as the one given 
    in the env.example will suffice. Otherwise use your production secret key.
    
Build Arguments
-------------------------------

BUILD_ENV:
    Argument used to determine what dependencies and scripts to run when installing
    dependencies, populating databases, and setting ``DJANGO_SETTINGS_MODULE``. Values:
    ``local``, ``production``, and ``test``.

CHROMEDRIVER_VERSION:
    Argument used to override the version of Chromedriver to install, which defaults to
    the Chromedriver version returned by ``https://chromedriver.storage.googleapis.com/LATEST_RELEASE_X``
    (where ``X`` is the version number of the installed Chrome version).


Building Your Docker Containers
-------------------------------

This next section assumes you have downloaded ``docker`` and ``docker-compose``.
Additionally it assumes you have a ``.env`` file in the root directory of this 
project, a template of variables needed can be found under ``env.example``.

To configure and run your environment you must run 2 commands in the root directory of MetaCI
Note that docker-compose build will take some significant time to build the first time but will
be much faster for subsequent builds. It is also important to note that once you bring 
up the web application it will take roughly 60 seconds to fully compile.
::
    
    docker-compose build

Running Your Docker Containers
------------------------------
MetaCI's docker container comes out of the box with development test
data and the creation of a default admin user.

If you would like to disable this functionality please add a `DJANGO_SETTINGS_MODULE` environment variable
in the web service section of the docker-compose file to set it from its default value (set in Dockerfile) from
`config.settings.local` to `config.settings.production`.
For examples of how to do this please see `setting docker-compose environment variables`_.

.. _setting docker-compose environment variables: https://docs.docker.com/compose/environment-variables/

Then run the following command:
::

    docker-compose up -d 
    or 
    docker-compose up (for debug mode)

After running this command which will take a couple minutes on startup visit ``localhost:8000/admin/login``
and login with the following credentials if DJANGO_SETTINGS_MODULE is config.settings.local:

username:
    ``admin``
password:
    ``password``

From here you should be able to run builds. However note that this default account will not be created 
when BUILD_ENV is set to production

Docker Commands
---------------
To stop your virtual containers run the following command:
The docker-compose stop command will stop your containers, but it won’t remove them.
::

    docker-compose stop

To start your virtual containers run the following command:
::

    docker-compose start

To bring your virtual containers up for the first time run the following command:
::

    docker-compose up -d

To bring your virtual containers down run the following command:

.. warning:: The docker-compose down command will stop your containers, 
    but also removes the stopped containers as well as any networks that were created.

::

    docker-compose down
    
Removes stopped service containers. To remove your stopped containers enter the following commands

.. warning:: This will destroy anything that is in the virtual environment, 
    however the database data will persist 

::

    docker-compose rm

(then enter ``y`` when prompted. If you would like to clear the database as well include a -v flag i.e. ``docker-compose down -v``)

To view all running services run the following command:

::
    
    docker-compose ps

If you'd like to test something out manually in that test environment for any reason you can run the following:
In order to run relevant management commands like `manage.py makemigrations`, or if you'd like to test 
something out manually in that test environment for any reason you can run the following:

::

    docker-compose exec web bash

This will drop you into a bash shell running inside your container, where can execute commands.

You can also run commands directly:
::
    
    docker-compose exec web python manage.py makemigrations

Docker development using VS Code
--------------------------------

Because front-end and back-end dependencies are installed in a Docker container
instead of locally, text editors that rely on locally-installed packages (e.g.
for code formatting/linting on save) need access to the running Docker
container. `VS Code`_ supports this using the `Remote Development`_ extension
pack.

Once you have the extension pack installed, when you open the MetaShare folder
in VS Code, you will be prompted to "Reopen in Container". Doing so will
effectively run ``docker-compose up`` and reload your window, now running inside
the Docker container. If you do not see the prompt, run the "Remote-Containers:
Open Folder in Container..." command from the VS Code Command Palette to start
the Docker container.

A number of project-specific VS Code extensions will be automatically installed
for you within the Docker container. See `.devcontainer/devcontainer.json
<.devcontainer/devcontainer.json>`_ and `.devcontainer/docker-compose.dev.yml
<.devcontainer/docker-compose.dev.yml>`_ for Docker-specific VS Code settings.

The first build will take a number of minutes, but subsequent builds will be
significantly faster.

Similarly to the behavior of ``docker-compose up``, VS Code automatically runs
database migrations and starts the development server/watcher. To run any local commands, 
open an `integrated terminal`_ in VS Code (``Ctrl-```) and use any of the development
commands (this terminal runs inside the Docker container and can run all the commands that can be run in
RUNNING.RST and CONTRIBUTING.RST)::

    $ python manage.py migrate  # run database migrations
    $ yarn serve  # start the development server/watcher

For any commands, when using the VS Code integrated terminal inside the
Docker container, omit any ``docker-compose run --rm web...`` prefix, e.g.::

    $ python manage.py promote_superuser <your email>
    $ yarn test:js
    $ python manage.py truncate_data
    $ python manage.py populate_data

``yarn serve`` is run for you on connection to container. You can view the running app at
`<http://localhost:8080/>`_ in your browser.

For more detailed instructions and options, see the `VS Code documentation`_.

.. _VS Code: https://code.visualstudio.com/
.. _Remote Development: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack
.. _integrated terminal: https://code.visualstudio.com/docs/editor/integrated-terminal
.. _VS Code documentation: https://code.visualstudio.com/docs/remote/containers
