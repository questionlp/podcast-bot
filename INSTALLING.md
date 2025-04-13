# Installing and Running the podcast-bot Application

## Installing Dependencies

It is highly recommended that you set up a virtual environment for this project and install the dependencies within the virtual environment. The following example uses Python's `venv` module to create the virtual environment, once a copy of this repository as been cloned locally.

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Configurating the Application

All of the application configuration settings, along with the podcast feeds, by default, are read from the `settings.json` file located in the root of the application folder. A simple example file, `settings.dist.json`, that can be used to get you started.

The following sections go over the different sections, including the core application and podcast feed settings. Each podcast feed will have its own section for Mastodon and Bluesky account information that allows you to post new episodes to different accounts for each podcast. Please note that a maximum of one Mastodon account and one Bluesky account can be defined for each podcast feed.

### Application Configuration Settings

At the top level of the application settings JSON file has application-wide configuration keys.

| Key Name | Description |
| -------- | ----------- |
| database_file | Location of the SQLite database file that will be used to store episodes that the application has already been processed. (Default: `dbfiles/feed_info.sqlite3`) |
| database_clean_days | Number of days to keep records in the SQLite database. Used by the clean-up function to remove older entries. This value should be greater than the value set for `recent_days`. (Default: `90`) |
| log_file | Path for the log file the application used for recording event logs. (Default: `logs/app.log`) |
| user_agent | User Agent string to provide when retrieving a podcast feed. (Default: `Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0`). |
| feeds | An array containing [configuration settings](#feed-configuration-settings) for each podcast feed the application will loop through. |

### Feed Configuration Settings

The top-level `feeds` configuration key contains an array of objects, each containing configuration settings for each podcast feed the application will loop through. The array must contain at least one podcast feed.

| Key Name | Description |
| -------- | ----------- |
| name | Name of the podcast to be included in the post. |
| short_name | Short podcast identifier used to tag each entry in the database. |
| feed_url | URL for the podcast feed to retrieve and parse episodes. |
| enabled | Flag to set whether or enable or disable processing of the podcast feed (Default: `true`) |
| recent_days | Number of days in a podcast RSS feed to process. Any episodes older than that will be skipped. (Default: `5`) |
| max_episodes | Maximum number of episodes to retrieve from the podcast feed and process. (Default: `20`) |
| guid_filter | String used as a filter episode GUIDs values to include and exclude GUIDs that to not include the string. (Default: `""`) |
| bluesky_settings | An object containing [configuration settings](#bluesky-configuration-settings) for the Bluesky account used to publish posts. |
| mastodon_settings | An object containing [configuration settings](#mastodon-configuration-settings) for the Mastodon account used to publish posts. |

### Bluesky Configuration Settings

By default, the application will publish new episodes to Bluesky if there is a value set in both the `username` and `password` configuration keys. If neither are set, the application will return an error and exit.

If you do not want the application to publish to Bluesky, you will need to set the `enabled` configuration key to `false`.

You will need to create an app password for the Bluesky account you would like to use to publish new episodes. To create an app password, log into Bluesky with the account you want to use, then go to **Settings**, then **Privacy and Security**, then click on **+ Add App Password**. Enter in a name for the new app password, the click on **Next**. Bluesky will generate an app password that you'll need for this application.

Due to the experimental nature of the session token feature in the application, it is highly recommended to keep the `use_session_token` configuration key set to `false`.

| Key Name | Description |
| -------- | ----------- |
| enabled | Enable posting new episodes to Bluesky. (Default: `true`) |
| username | Bluesky account username, excluding the leading `@`. |
| app_password | App password for the Bluesky account. |
| session_file | Location of the SQLite database file used to store Bluesky session tokens. (Default: `dbfiles/bluesky_session.sqlite3`) |
| use_session_token | Enable the use of Bluesky session token to connect to Bluesky. (Default: `false`) |
| api_url | The base API URL for Bluesky. (Default: `https://bsky.social`) |
| template_file | Path for the Jinja2 template file that will be used to format the post. (Default: `templates/post-bluesky.txt.jinja`) |
| max_title_length | Maximum length (in characters) of the podcast episode title to be included in the post. (Default: `100`) |
| max_description_length | Maximum length (in characters) of the podcast episode description to be included in the post. (Default: `150`) |

### Mastodon Configuration Settings

By default, the application will publish new episodes to Mastodon. In order to publish posts to Mastodon, you will need to set the `api_url` configuration key, which is usually the base URL for your Mastodon instance, though you may want to verify with your instance administrator.

For authentication, you can either use OAuth authentication or create an application under your account preferences. The latter is the recommended option since it is easier to set up.

To use OAuth authentication, you will need to create a user credential secrets file using the steps provided in the [Mastodon.py](https://mastodonpy.readthedocs.io/en/stable/) documentations. The path to the secrets file needs to be set in the `secrets_file` configuration key and the `use_oauth` configuration key needs to be set to `true`.

To create a Mastodon application for your account, log into your Mastodon instance using the account you want to use, then go to **Preferences**, then **Development**, and create a **New application**.

The **Application name** will be displayed as the application used to publish new posts. The **Application website** should be a valid URL, either to the URL for user profile page, the Mastodon instance, or a link back to this repository. The default value for **Redirect URI** will work. For **Scopes**, the both **read** and **write** should be enabled.

Once you submit the new application form, a client key, client secret and an access token should be generated. The latter two will need to be entered in the `client_secret` and `access_token` configuration keys and `use_oauth` needs to be set to `false`.

If you do not want the application to publish to Mastodon, you will need to set the `enabled` configuration key to `false`.

| Key Name | Description |
| -------- | ----------- |
| enabled | Enable posting new episodes to Mastodon. (Default: `true`) |
| api_url | The base API URL for your Mastodon instance. Refer to your Mastodon instance for the appropriate URL to use. |
| use_oauth | Set whether or not a Mastodon secrets file will be used for authenticiation. (Default: `false`) |
| secrets_file | OAuth secret file that will be used to authenticate your Mastodon user account against your Mastodon server. Required when `use_oath` is set to `true`. (Default: `secrets/usercred.secret`) |
| client_secret | Mastodon API client secret used for authentication. Not required when using OAuth authentication. |
| access_token | Mastodon API access token used for authentiication. Not required when using OAuth authentication. |
| template_file | Path for the Jinja2 template file that will be used to format the post. (Default: `templates/post-mastodon.txt.jinja`) |
| max_title_length | Maximum length (in characters) of the podcast episode title to be included in the post. (Default: `100`) |
| max_description_length | Maximum length (in characters) of the podcast episode description to be included in the post. (Default: `275`) |

## Running the Application

To run the application, activate the virtual environment if one was created, then run the following command:

```bash
python3 podcast_boy.py
```

By default, the application will read configuration settings from the `settings.json` file located in the application root directory and will automatically clean up podcast entries from the application's SQLite database that are older than 90 days.

### Application Command Line Flags and Options

The application has several command line flags and options available:

| Flag/Option | Description |
| ----------- | ----------- |
| `-s`, `--settings` | Set a custom path for the feeds JSON file that contains application settings and podcast feeds. (Default: `settings.json`) |
| `--debug` | Runs the application in debug mode with more verbose logging. |
| `--dry-run` | Run the application in dry run mode, which skips creating or updating database entries or posts. It will create an empty SQLite database if one does not exist. |
| `--skip-clean` | Skips the database clean-up step to remove old entries. This step is also skipped if the `--dry-run` flag is also set. |
