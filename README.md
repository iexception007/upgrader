# need process problem.
```
v1.4.9
host_path: grframeworkv2
driver:
  get_input: GLO

---------------->

v1.5.0
host_path:
  get_input: GLO
driver: ''

```

# gen preenv
```
pip freeze > requirements.txt
pip install -r requirements.txt
```

# install
```
pip install logging
pip install pymsql
pip install pyyaml
pip install ConfigParser
```

# edit the config
```
[mysql]
host = dev-7
port = 3307
username = root
password = password
```
# run
1. backup the special database to ./backup  
2. update the yaml and save to the table  
```
make build
make run
```