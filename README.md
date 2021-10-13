<img src="https://imgur.com/OFVhKoQ.png" alt="Confugiradores"/>
Bot de discord programado para el servidor de Confugiradores.
<a href="https://discord.com/invite/9aqHgCT7jm">Confugiradores Discord</a>

## Comandos

El bot tiene comandos variados para moderar, pasarlo bien o añadir funcionalidades, aquí tienes la lista completa de los que hay actualmente:

* Mute
* Unmute
* Kick
* Ban
* Unban
* Clear
* Say
* Send
* Confugiradores
* Cumple
* Nick
* Spank
* Bonk
* Chad
* Invite
* Preffixes
* Settings
* Reaction

Para mas informacion de lo que hace cada función unete al <a href="https://discord.com/invite/9aqHgCT7jm">Discord</a> y usa $help.

## Instalación

Si quieres crear una copia del bot eres libre de hacerlo y cambiarlo a tu gusto, estaría genial que mencionases mi trabajo pero no es obligatorio.
Para instalarlo crea un clon del repositorio e instala con pip los siguientes modulos:

```sh
pip install discord.py emojis mariadb Pillow datetime dotenv
```
Para que el bot funcione correctamente crea un archivo de texto en la raiz del proyecto llamado ".env" con las siguientes opciones:
```sh
TOKEN='Token de tu bot de discord'
AUTHOR='Aqui tienes que introducir tu discord tag foo#0000'
CHANNEL='Canal para sugerencias y bugs (del bot), no es necesario.'
USERNAME='Usuario con permisos en la base de datos, no es recomendable que sea root'
PASSWORD='Contraseña del USERNAME'
HOST='Dirección de la base de datos'
PORT='Puerto de la base de datos, por defecto será 3306'
DATABASE='Nombre de la base de datos'
```
A continuacion tienes que configurar la base de datos, sustituye los datos entre <angulos> por los datos que has introducido en .env.
El gestor de bases de datos usado en este proyecto es mariadb, si ya lo tienes instalado crea una nueva base de datos con:
```sh
CREATE DATABASE <DATABASE>;
```
A continucacion otorga los permisos a la cuenta del bot, para ello.
```sh
GRANT ALL PRIVILEGES ON <DATABASE>  TO '<USERNAME>'@'<HOST>' IDENTIFIED BY '<PASSWORD>';
```
Para cualquier duda o sugerencia no dudes en contactar conmigo!!
## Licencia
    
Este proyecto se encuentra bajo la licencia GPLv3, esto significa:
1. Puedes, copiar, modificar y distribuir este software.
2. You have to include the license and copyright notice with each and every distribution.
3. Puedes usar este software para propositos comerciales.
4. Si modificas el código debes indicar que has modificado.
5. Cualquier modificacion DEBE ser distribuida bajo la licencia GPLv3.
6. Este software carece de garantia por lo que tanto el autor como la licencia no se hacen responsables de ningun daño causado por el software.
            
