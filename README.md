Playing around with using an LLM and vale.

Vale runs on /docs/content/guides/use-case/

Then it goes issue-by-issue passing context to the LLM to get a suggestion.


1. Rename .env.example to .env.
2. Add your Gemini API key inside .env
3. Clone https://github.com/docker/docs in the same directory
4. docker compose up --build
