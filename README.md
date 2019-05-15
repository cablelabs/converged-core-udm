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
