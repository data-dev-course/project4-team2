## Backend
- Write backend application in /services/backend/src folder
  - for tests, use /services/backend/tests folder
### to start
- install `pip install pipenv` if you don't have
- run `pipenv install` or `pipenv shell`
- execute entrypoint.py file ; `python entrypoint.py` 
- go to http://0.0.0.0:8000/docs

### to build (docker image)
- run `docker-compose up`
- go to http://0.0.0.0:8081/docs to see the Swagger API docs

## Frontend
- Vite+React+Javascript
- tailwindcss for style
### to start
- in the /services/frontend folder
- `npm install`
- `npm run dev`