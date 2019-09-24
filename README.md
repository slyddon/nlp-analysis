## 80-days-analysis
***

This is a demonstration project showing how to use a dockerised environment to perform a contained analysis. In it we perform some nlp on the novel _Around the World in 80 Days_.

### Development
This project uses a docker container within which we perform the analysis, the source scripts are mounted as volume. A persistant database is also created for storing location information.

To set up the development environment follow these steps. We presume you have docker available and volume sharing configured.

* Volume sharing on Windows with a postgres container directly through docker-compose has problems so a volume needs to be instantiatiated separately. Run: `docker volume create pgdata`
* Run `docker-compose up --build` to bring up the containers and build the images.

A jupyter notebook instance is exposed on port 8888 with a password token as specified in the `docker-compose.yaml`. A postgres db instance is exposed on port 5432.

Go to `https://localhost:8888/lab?token=p`.

### Running the analysis
The notebook `route_analysis.ipynb` demonstrates the use of entity recognition to extract the locations visited in the novel.
