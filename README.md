# podcast-bot

podcast-bot is a Python application that parses a podcast RSS/Atom feed and publishes new episodes to an account on either Bluesky or Mastodon, or both.

## Notes Regarding bluesky-podcast-bot and mastodon-podcast-bot

This application combines the codebase of both [bluesky-podcast-bot](https://github.com/questionlp/bluesky-podcast-bot) and [mastodon-podcast-bot](https://github.com/questionlp/mastodon-podcast-bot) applicaitons into a unified application. Once development of this application has reached a stable point, the original Mastodon and Bluesky Podcast Bot applications will be deprecated.

Migrating from either application will require migrating the former feeds JSON configuration file to the new application settings JSON file, `settings.json`.  

## Requirements

Prior to version 1.3.0, Python 3.10 through 3.13 is supported. Starting with version 1.3.0, Python 3.10 through 3.14 is supported.

In addition, you will need authentication information for an account on either Mastodon or Bluesky in order to publish posts.

## Installing and Running the Application

For more information on installing, configuring and running the application, please refer to the [INSTALLING.md](./INSTALLING.md) file included in the repository.

## Development

Use the included `requirements-dev.txt` to install both the application and development dependencies.

The project makes generous use to type hints to help with code documentation and can be very helpful when using Python language servers in Visual Studio Code, tools such as [mypy](http://mypy-lang.org), and others.

For code linting and formatting, the project makes use of Ruff and Black.

## Code of Conduct

This project follows the code of conduct pledge defined by the [Contributor Covenant 3.0 Code of Conduct](CODE_OF_CONDUCT.md).

## AI Generated Code

Please note that this project does not accept pull requests or bugfixes that include code that has been partially or wholly generated using AI.

## License

This project is licensed under the terms of the [MIT License](LICENSE).
