# converged-core-udm
Prototype UDM for Converged Core

## To run

Execute the following command:

```
python udm_api/app.py
```

## Notes

Here are some notes from @dschrimpsher:

1.  I had to make the $ref absolute path witch sucks but there is a lot of debate going on on connexion (and other places) on the best way to use multiple files.

2.  The functions don't do anything yet and I am not sure excatly how to get a token since the oauth references a api/yaml file I don't have.

3. I used a virtual env in pycharm. So you may need to do a pip install or whatever you normally do and get all the libraries.  I will (soon) setup a requirements, setup.cfg and such so that goes away but ...


## To build with Docker, execute:

```bash
docker build -t convergedcore/udm_api .
```

### To run in the foreground and remove when stopped:
```bash
docker run -it --rm -p 8080:8080 convergedcore/udm_api
```

### To run in background:
```bash
docker run -d --name udm_api -p 8080:8080 convergedcore/udm_api
```

## Swagger UI

The Swagger UI is available for both the NUDM-UECM and the NUDM-SDM. Assuming the API is running on localhost:8080, the endpoints are:

  * http://localhost:8080/nudm-uecm/v1/ui/
  * http://localhost:8080/nudm-sdm/v1/ui/