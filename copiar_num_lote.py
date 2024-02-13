import xmlrpc.client
import ssl
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="copiar_num_lote.log",
    filemode="w",
)

user_o = "Nelsonjr"  # el usuario de odoo origen
pwd_o = "Nelsonjr"  # contrasenia de usuario odoo origen

user_d = "Nelsonjr"  # el usuario de odoo destino
pwd_d = "Nelsonjr"  # contrasenia de usuario destino

dbname_o = "lared.devman.com.ar"  # nombre de base de datos origen
dbname_d = "lared-rma-test.devman.com.ar"  # nombre de base de datos destino

web_o = "https://lared.devman.com.ar/"  # ip o dir web del origen
web_d = "https://lared-rma-test.devman.com.ar/"  # ip o dir web del destino
# datos de los modelos y campos
model_o = "stock.production.lot"  # nombre del modelo de origen
model_d = "stock.production.lot"  # nombre del modelo del destino
idant_o = "id"  # TO DO  generar el x_id_anterior nombre del campo a usar en el destino para almacenar id anterior, dejar vacio si no se usa. (tiene que ser un campo existente en el modelo model_d)
# este campo hay que crearlo en el modelo
campos = [
    "name",
    "ref",
    "product_id",
    "product_qty",
    "warranty_exp_date",
]
condi1_o = [("id", ">", "0")]

gcontext = ssl._create_unverified_context()

#########? ORIGEN
sock_common_o = xmlrpc.client.ServerProxy(web_o + "xmlrpc/common", context=gcontext)
uid_o = sock_common_o.login(dbname_o, user_o, pwd_o)
#########?


#########? DESTINO
# Get the uid destino de los datos
sock_common_d = xmlrpc.client.ServerProxy(web_d + "xmlrpc/common", context=gcontext)
uid_d = sock_common_d.login(dbname_d, user_d, pwd_d)
#########?

# reemplazar el valor de la ip o url del servidor de origen con su puerto
sock_o = xmlrpc.client.ServerProxy(web_o + "/xmlrpc/object", context=gcontext)

# reemplazar el valor de la ip o url del servidor de destino con su puerto
sock_d = xmlrpc.client.ServerProxy(web_d + "xmlrpc/object", context=gcontext)

logging.info("===========================================")
logging.info("Se van a importar los siguientes registros:")
logging.info("Web de origen..: %s", web_o)
logging.info("Modelo a migrar: %s", model_o)
logging.info("-------------------------------------------")
logging.info("Se van a actualizar/crear los siguientes registros:")
logging.info("Web de destino.:  %s", web_d)
logging.info("Modelo migrado.:  %s", model_d)
logging.info("Campo id anter.:  %s", idant_o)
logging.info("===========================================")

#! Busca todos los registros que hay en el modelo de origen, segun la condicion que le hemos pasado
registro_ids_o = sock_o.execute(dbname_o, uid_o, pwd_o, model_o, "search", condi1_o)

# Iniciar los contadores
x, j, ec, ea = 0, 0, 0, 0

for i in registro_ids_o:
    #! Obtiene registros
    registro_data_o = sock_o.execute(dbname_o, uid_o, pwd_o, model_o, "read", i, campos)
    logging.info("Obteniendo registros...")

    #! Obtengo id y name del registro de la base de origen
    clave, nombre_o, product_id_o = (
        registro_data_o[0]["id"],
        registro_data_o[0]["name"],
        registro_data_o[0]["product_id"],
    )

    logging.info("Registro Obtenido: %s", registro_data_o[0]["product_id"])
    registro_id_d = sock_d.execute(
        dbname_d, uid_d, pwd_d, model_d, "search", [("name", "=", nombre_o)], 0, 1
    )
    product_id_d = sock_d.execute(
        dbname_d,
        uid_d,
        pwd_d,
        "product.template",
        "search",
        [("name", "=", registro_data_o[0]["product_id"][1])],
    )

    # if registro_id_d:
    #     pass
    #     # logging.info("HAY REGISTRO... VAMOS A ACTUALIZAR")
    #     # try:
    #     #     return_id  = sock_d.execute(dbname_d, uid_d, pwd_d, model_d, "write", registro_id_d, valores_update)
    #     #     logging.info("ACTUALIZADO CON EXITO: %s", registro_data_o[0]["product_id"])
    #     # except Exception as e:
    #     #     logging.error("================================================")
    #     #     logging.error(e)
    #     #     logging.error("================================================")
    #     #     ea += 1
    #     # x += 1
    if not registro_id_d and product_id_d:
        logging.info("NO HAY REGISTRO... VAMOS A CREARLO")
        logging.info(product_id_d)
        valores_update = {
            "name": registro_data_o[0]["name"],
            "ref": registro_data_o[0]["ref"],
            "product_qty": registro_data_o[0]["product_qty"],
            "warranty_exp_date": registro_data_o[0]["warranty_exp_date"],
            "product_id": product_id_d[0],
            "company_id": 1
        }
        try:
            return_id = sock_d.execute(
                dbname_d, uid_d, pwd_d, model_d, "create", valores_update
            )
            logging.info("CREADO")
        except Exception as e:
            logging.error("================================================")
            logging.error(e)
            logging.error("================================================")
            ec += 1
        j += 1

logging.info("Cantidad de registros actualizados: %s", x)
logging.info("Cantidad de actualizados con error: %s", ea)
logging.info("Cantidad de registros creados: %s", j)
logging.info(" Cantidad de errores al crear: %s", ec)
