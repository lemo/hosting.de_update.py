# hosting.de_update.py
update your dns settings on hosting.de via REST API

https://github.com/lemo/hosting.de_update.py

## caveats
updating a TXT record requires escaping the data with backslash e.g. \\\"DATA\\\" especially with selective remove

## TODO
fix --content unicode problems
