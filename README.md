# podcast-bot

podcast-bot is a Python application that parses a podcast RSS/Atom feed and publishes new episodes to an account on either Bluesky or Mastodon, or both.

## Notes Regarding bluesky-podcast-bot and mastodon-podcast-bot

This application combines the codebase of both [bluesky-podcast-bot](https://github.com/questionlp/bluesky-podcast-bot) and [mastodon-podcast-bot](https://github.com/questionlp/mastodon-podcast-bot) applicaitons into a unified application. Once development of this application has reached a stable point, the original Mastodon and Bluesky Podcast Bot applications will be deprecated.

Migrating from either application will require migrating the former feeds JSON configuration file to the new application settings JSON file, `settings.json`.  

## Requirements

This project requires Python 3.10 or higher.

In addition, you will need authentication information for an account on either Mastodon or Bluesky in order to publish posts.

### Mastodon

For Mastodon accounts, the application supports either using OAuth authentication, or using a client secret and an access token.

### OAuth Authentication

To create the Mastodon OAuth secret file, refer to the [Mastodon.py](https://mastodonpy.readthedocs.io/en/stable/) documentation for instructions. Any secret files should be stored under `secrets/`, as any file (with exception of the included [README.md](secrets/README.md) file) are filtered out by way of the repository's `.gitignore`.

### Client Secret and Access Token

To generate a client secret and access token, log into your Mastodon instance using the account you want to use, then go to **Preferences**, then **Development**, and create a **New application**.

The **Application name** will be displayed as the application used to publish new posts. The **Application website** should be a valid URL, either to the URL for user profile page, the Mastodon instance, or a link back to this repository. The default value for **Redirect URI** will work. For **Scopes**, the both **read** and **write** should be enabled.

Once you submit the new application form, a client key, client secret and an access token should be generated. The latter two values will be needed for this application.

## Bluesky

For Bluesky accounts, the application currently only supports using app passwords.

### App Password

To create an app password, log into Bluesky with the account you want to use, then go to **Settings**, then **Privacy and Security**, then click on **+ Add App Password**. Enter in a name for the new app password, the click on **Next**. Bluesky will generate an app password that you'll need for this application.

## Installing

It is highly recommended that you set up a virtual environment for this project and install the dependencies within the virtual environment. The following example uses Python's `venv` module to create the virtual environment, once a copy of this repository as been cloned locally.

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Running the Application

Unlike the preceding Mastodon and Bluesky Podcast Bot applications, this application only supports a JSON configuration file, `settings.json`. The use of an `.env` environment file is no longer supported.

The application will automatically create the SQLite version 3 database if one does not already exist.

### Command-Line Flags and Options

There are several flags and options that can be set through the command line:

| Flag/Option | Description |
| ----------- | ----------- |
| `-s`, `--settings` | Set a custom path for the feeds JSON file that contains application settings and podcast feeds. (Default: `settings.json`) |
| `--debug` | Runs the application in debug mode with more verbose logging. |
| `--dry-run` | Run the application in dry run mode, which skips creating or updating database entries or posts. It will create an empty SQLite database if one does not exist. |
| `--skip-clean` | Skips the database clean-up step to remove old entries. This step is also skipped if the `--dry-run` flag is also set. |

### Configuration File

The `feeds.json` file contains application configuration settings for the application, podcast feeds, and Mastodon and/or Bluesky settings. An example configuration file, `feeds.dist.json` is included in this repository.

### Application Configuration Keys

| Key Name | Description |
| -------- | ----------- |
| database_file | Location of the SQLite database file that will be used to store episodes that the application has already been processed. (Default: `dbfiles/feed_info.sqlite3`) |
| database_clean_days | Number of days to keep records in the SQLite database. Used by the clean-up function to remove older entries. This value should be greater than the value set for `recent_days`. (Default: `90`) |
| bluesky_session_file | Location of the SQLite database file used to store Bluesky session tokens. (Default: `dbfiles/bluesky_session.sqlite3`) |
| log_file | Path for the log file the application used for recording event logs. (Default: `logs/app.log`) |
| user_agent | User Agent string to provide when retrieving a podcast feed. (Default: `Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0`). |
| feeds | List of [Feed configuration keys](#feed-configuration-keys) containing podcast feeds and associated settings. |

#### Feed Configuration Keys

| Key Name | Description |
| -------- | ----------- |
| name | Name of the podcast to be included in the post. |
| short_name | Short podcast identifier used to tag each entry in the database. |
| feed_url | URL for the podcast feed to retrieve and parse episodes. |
| enabled | Flag to set whether or enable or disable processing of the podcast feed (Default: `true`) |
| recent_days | Number of days in a podcast RSS feed to process. Any episodes older than that will be skipped. (Default: `5`) |
| max_episodes | Maximum number of episodes to retrieve from the podcast feed and process. (Default: `20`) |
| guid_filter | String used as a filter episode GUIDs values to include and exclude GUIDs that to not include the string. (Default: `""`) |
| bluesky_settings | [Bluesky configuration keys](#bluesky-configuration-keys) for a Bluesky account to use to publish posts. |
| mastodon_settings | [Mastodon configuration keys](#mastodon-configuration-keys) for a Mastodon account to use to publish posts. |

#### Bluesky Configuration Keys

| Key Name | Description |
| -------- | ----------- |
| enabled | Enable posting new episodes to Bluesky. (Default: `true`) |
| username | Bluesky account username, excluding the leading `@`. |
| app_password | App password for the Bluesky account. |
| use_session_token | Enable the use of Bluesky session token to connect to Bluesky. (Default: `false`) |
| api_url | The base API URL for Bluesky. (Default: `https://bsky.social`) |
| template_file | Path for the Jinja2 template file that will be used to format the post. (Default: `templates/post-bluesky.txt.jinja`) |
| max_description_length | Maximum length (in characters) of the podcast episode description to be included in the post. (Default: `150`) |

#### Mastodon Configuration Keys

| Key Name | Description |
| -------- | ----------- |
| enabled | Enable posting new episodes to Mastodon. (Default: `true`) |
| api_url | The base API URL for your Mastodon instance. Refer to your Mastodon instance for the appropriate URL to use. |
| use_oauth | Set whether or not a Mastodon secrets file will be used for authenticiation. (Default: `false`) |
| secrets_file | OAuth secret file that will be used to authenticate your Mastodon user account against your Mastodon server. Required when `use_oath` is set to `true`. (Default: `secrets/usercred.secret`) |
| client_secret | Mastodon API client secret used for authentication. Not required when using OAuth authentication. |
| access_token | Mastodon API access token used for authentiication. Not required when using OAuth authentication. |
| template_file | Path for the Jinja2 template file that will be used to format the post. (Default: `templates/post-mastodon.txt.jinja`) |
| max_description_length | Maximum length (in characters) of the podcast episode description to be included in the post. (Default: `275`) |

## Development

Use the included `requirements-dev.txt` to install both the application and development dependencies.

The project makes generous use to type hints to help with code documentation and can be very helpful when using Python language servers in Visual Studio Code, tools such as [mypy](http://mypy-lang.org), and others.

For code linting and formatting, the project makes use of Ruff and Black.

## Code of Conduct

This project follows version 2.1 of the [Contributor Covenant's](https://www.contributor-covenant.org) Code of Conduct.

## License

This project is licensed under the terms of the [MIT License](LICENSE).
