# docker build -t twstockanalyzer_image:v1 -f ./dockerfile/twstockanalyzer.Dockerfile .
docker run -v /path/on/your/desktop:/app/output twstockanalyzer_image:v1
docker run twstockanalyzer_image:v1
