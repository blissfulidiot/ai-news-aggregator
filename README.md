What I want to build is an AI news aggregator where I can take multiple news sources and youtube videos and blog posts from example openai and anthropic as well as financial information from sites such as the sec and scrape those and put them into a database where we have a structure with sources and we have lets call them articles and i want to run a daily digest where we take all the articles from that time frame and we can make a llm summary and based on the user system prompt we can have those articles and we can make short snipits with a link to the source for the user for the youtube videos we can create a list of channels and get the latest videos from those channels we can probably use a youtube rss feed for that and for the blog posts we can have urls we can scrape for that. I want everything built in a python backend, I want to use a postgres sql database, i want to use sqlalchamey to define the database models and create the tables, i want the project structure to be an app folder where all the app logic is in, i want a docker folder for where we first create the very minimal set of postgres sql database, for a good start. later down the line we want to deploy the whole app to render and we can schedule it every 24 hours to run reports and when we create the daily digest i want it to be sent to my personal inbox.

https://openai.com/news/

https://www.anthropic.com/engineering

https://www.anthropic.com/research

