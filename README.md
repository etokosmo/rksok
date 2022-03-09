<h1 align="center">РКСОК Protocol</h1>
RKSOK - Russian lite version of analogue of the HTTP protocol.

## About

<p>The basis of the project is a notebook where you can check the person's phone number in the notebook, write down the person's number or delete the person's number from the notebook.</p>

<p>RKSOK version 1.0 consists of four commands.</p>

* ОТДОВАЙ - to return data / <b>GET</b>
* УДОЛИ - to delete data / <b>DELETE</b>
* ЗОПИШИ - for creating and updating data / <b>WRITE</b>
* АМОЖНА? - to obtain permission to process the command from special authorities / <b>Request to server-check</b>

## Description of the RKSOK 1.0 protocol

### GET Request:
```
ОТДОВАЙ Alexey РКСОК/1.0
```
If Alexey is in the notebook and the server-check approves the request, the server will return
```
НОРМАЛДЫКС РКСОК/1.0
89012345678
```
If Alexey is not in the notebook
```
НИНАШОЛ РКСОК/1.0
```
If the server-check refuses the request, the server will return message from server-check, f.e.
```
НИЛЬЗЯ РКСОК/1.0
Уже едем
```
### WRITE Request:
```
ЗОПИШИ Alexey РКСОК/1.0
89012345678
```
If the server-check approves the request, the server will return
```
НОРМАЛДЫКС РКСОК/1.0
```
### DELETE Request:
```
УДОЛИ Alexey РКСОК/1.0
```
If Alexey is in the notebook and the server-check approves the request, the server will return
```
НОРМАЛДЫКС РКСОК/1.0
```
If Alexey is not in the notebook
```
НИНАШОЛ РКСОК/1.0
```
### Request to server-check:
The request that came to the server, we must send it to the server-check, f.e.
```
ЗОПИШИ Alexey РКСОК/1.0
89012345678
```
Request to server-check:
```
АМОЖНА? РКСОК/1.0
ЗОПИШИ Alexey РКСОК/1.0
89012345678
```
Respose from server-check:
<br>
OK:
```
МОЖНА РКСОК/1.0
```
NOT_APPROVED:
```
НИЛЬЗЯ РКСОК/1.0
Что ещё за Alexey такой? Он тебе зачем?
```
### Other:
Wrong request
```
НИПОНЯЛ РКСОК/1.0
```
End of request
```
\r\n\r\n
```
for example
```
ЗОПИШИ Alexey РКСОК/1.0\r\n89012345678 — мобильный\r\n02 — рабочий\r\n\r\n
```
Max length of name
```
30 characters
```

## Configuration

* Python version: <b>3.10</b>
* Libraries: <b>requirements.txt</b>
* Server: <b>0.0.0.0</b> PORT: <b>8888</b>
* Server-check: <b>vragi-vezde.to.digital</b> PORT <b>51624</b>

## Start server

```
python3.10 -m venv env
source env/bin/activate

pip install -r requirements.txt
python server.py
```

## Thanks to

* [Alexey Goloburdin](https://stepik.org/users/366827129)
* [Course "Основы компьютерных и веб-технологий с Python от Диджитализируй"](https://stepik.org/course/96018/info)
* Chat from course