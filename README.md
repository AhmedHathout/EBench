# EBench
An environment for testing and evaluating the theorem prover E. The
client communicates with the server via a socket to send commands and files so that the server can use them to run the
prover and provide the client with the results when asked to.

## Getting Started
1. Use `git clone https://github.com/ahmedHathout/EBench.git` to get a copy of the project on your machine or click clone or download on the project home page then click download ZIP.
2. Run `configure.py` script from the terminal by typing `./configure`. It is better to use the optional arguments too. type `./configure.py -h` to know more.
3. If you want to run the server on your machine go to `EBench/Server/` then type `./server.py`. There are some optional arguments too so type `./server.py -h` instead to know more about them.
4. If you want to run the client on your machine go to `Ebench/client/` then type `./client.py`. There are some optional arguments too so type `./client.py -h` instead to know more about them.

### Client
If you are running the client, you should use the command `help` to a list of all the instruciton that you can tell the server to execute. You can after that type the instruction followed by `-h` to know more about it.

### Server
The server just listens to the incoming connections and and executes the commands that come from the clients so there is nothing to type on its standard input.

## Resetting the server
If you want to delete all the output files that came from the server you can navigate to the main directory of the project which is `EBench` then type './reset`.
