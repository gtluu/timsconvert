This is a server to make timsconvert available on systems that might lack the dependencies.

To run the server we require docker and docker-compose

```
make server-compose-interactive
```

The server will be run at localhost:6521

To check that its running, go to 

```
http://localhost:6521/heartbeat
```
