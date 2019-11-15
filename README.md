# DocRotator
Implementation of automatic rotation of image of document scan

## Build and run docker container
docker build -t doc_rotator:latest .
docker run -d -p 5000:5000 doc_rotator:latest

## Usage
### Send image and saving result to json:
`curl -F "img=@[path_to_image] "Content-type: multipart/form-data" -X POST http://localhost:5000 > result.json`

### Convert json to image:
`python3 json2img.py`
