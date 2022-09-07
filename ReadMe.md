# How to run locally

### Prerequisites

Docker
Python

### Instructions

Step1

```
git clone https://github.com/datakind/united-way-211-forecast-app.git
cd "united-way-211-forecast-app"
```

Step 1a (FOR MAC m1)

```
export DOCKER_DEFAULT_PLATFORM=linux/arm64/v8
```

Step 2

```
docker build . -t uwwapp
docker run -p 5000:5000 -t uwwapp
```

Step 3

Go your browser and type:

```
http://localhost:5000
```
