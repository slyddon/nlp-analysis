## 80-days-analysis
***

This project performs nlp analysis on the novel _Around the World in 80 Days_.

### Development
This project uses a docker container to perform the analysis, the source scripts are mounted as volume. A persistant database is also created for storing location information.

To set up the development environment follow these steps. We presume you have docker available and volume sharing configured.

* Volume sharing on Windows with a postgres container has problems so a volume needs to be instantiatiated separately. Run: `docker volume create pgdata`
* Run `docker-compose up --build` to bring up the containers and build the images.

A jupyter notebook instance is exposed on port 8889. A postgres db instance is exposed on port 5432.
