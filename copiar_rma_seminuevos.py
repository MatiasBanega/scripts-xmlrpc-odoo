import xmlrpc.client
import ssl
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="copiar_rma_seminuevos.log",
    filemode="w",
)


#! DATOS DE ORIGEN
user_o = "Nelsonjr"
pwd_o = "Nelsonjr"
dbname_o = "lared.devman.com.ar"
web_o = "https://lared.devman.com.ar/"
model_o = "rma_seminuevos"
idant_o = "name"

#! DATOS DE DESTINO
user_d = "Nelsonjr"
pwd_d = "Nelsonjr"
dbname_d = "lared-rma-test.devman.com.ar"
web_d = "https://lared-rma-test.devman.com.ar/"
model_d = "rma_seminuevos"

#! CAMPOS DEL MODELO
campos = [
    "name",
    "productos_id",
    "stock_lot",
    "falla_aparente",
    "estado",
    "fecha_carga",
    "create_uid",
    "marca",
    "plu",
    "fecha_mod_estado",
    "proveedor",
    "orden_service",
    "fecha_ingreso",
    "fecha_retiro",
    "detalle",
    "costo",
    "estado_service",
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

sock_o = xmlrpc.client.ServerProxy(web_o + "/xmlrpc/object", context=gcontext)

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

registro_ids_o = sock_o.execute(dbname_o, uid_o, pwd_o, model_o, "search", condi1_o)

# Iniciar los contadores
x, j, ec, ea = 0, 0, 0, 0

for i in registro_ids_o:
    logging.info("cada registro de origen lo llamamos i, contiene lo siguiente: %s", i)
    logging.info(
        "Verificando en el origen el modelo:  %s,  el objeto con id:  %s", model_o, i
    )
    registro_data_o = sock_o.execute(dbname_o, uid_o, pwd_o, model_o, "read", i, campos)
    logging.info("Registro  Obtenido: %s", registro_data_o)

    clave, nombre_o = registro_data_o[0]["id"], registro_data_o[0]["name"]

    registro_id_d = sock_d.execute(
        dbname_d, uid_d, pwd_d, model_d, "search", [(idant_o, "=", nombre_o)]
    )

    if registro_data_o[0]["productos_id"]:
        product_id_destino = sock_d.execute(
            dbname_d,
            uid_d,
            pwd_d,
            "product.template",
            "search",
            [("name", "=", registro_data_o[0]["productos_id"][1])],
        )
    else:
        product_id_destino = []

    valores_update = {
        "name": registro_data_o[0]["name"],
        "falla_aparente": registro_data_o[0]["falla_aparente"],
        "estado": registro_data_o[0]["estado"],
        "fecha_carga": registro_data_o[0]["fecha_carga"],
        "create_uid": registro_data_o[0]["create_uid"],
        "marca": registro_data_o[0]["marca"],
        "plu": registro_data_o[0]["plu"],
        "fecha_mod_estado": registro_data_o[0]["fecha_mod_estado"],
        "orden_service": registro_data_o[0]["orden_service"],
        "fecha_ingreso": registro_data_o[0]["fecha_ingreso"],
        "fecha_retiro": registro_data_o[0]["fecha_retiro"],
        "detalle": registro_data_o[0]["detalle"],
        "costo": registro_data_o[0]["costo"],
        "estado_service": registro_data_o[0]["estado_service"],
    }
    if registro_data_o[0]["proveedor"]:
        #! BUSCAR PROVEEDOR SINO ENCUENTRA DAR COMO VACIO
        proveedor_d = sock_d.execute(
            dbname_d,
            uid_d,
            pwd_d,
            "res.partner",
            "search",
            [("name", "=", registro_data_o[0]["proveedor"][1])],
        )

        if proveedor_d:
            valores_update["proveedor"] = proveedor_d[0]
        else:
            valores_update["proveedor"] = False
    if product_id_destino:
        valores_update["productos_id"] = product_id_destino[0]
    else:
        valores_update["productos_id"] = False
    if registro_data_o[0]["stock_lot"]:
        stock_lot_d = sock_d.execute(
            dbname_d,
            uid_d,
            pwd_d,
            "stock.production.lot",
            "search",
            [("name", "=", registro_data_o[0]["stock_lot"][1])],
        )
        if stock_lot_d:
            valores_update["stock_lot"] = stock_lot_d[0]
        else:
            valores_update["stock_lot"] = False
    if registro_data_o[0]["create_uid"]:
        valores_update["create_uid"] = registro_data_o[0]["create_uid"][0]
    if registro_id_d:
        logging.info(
            "Encontrado en el nuevo servidor %s con nombre %s lo vamos a actualizar",
            clave,
            nombre_o,
        )
        # aca nombramos variables para luego llamarlas dentro de valores_update, en especial las que devuelven un diccionario.

        try:
            return_id = sock_d.execute(
                dbname_d, uid_d, pwd_d, model_d, "write", registro_id_d, valores_update
            )
            logging.warning("%s, EXITO AL ACTUALIZAR %s", return_id, nombre_o)
        except Exception as e:
            logging.error("================================================")
            logging.error(
                "Ha ocurrido un error al intentar crear el user: %s", nombre_o
            )
            logging.error(e)
            logging.error("================================================")
            ea += 1
        x += 1
    # si no se econtro el registro en el destino se crea
    else:
        logging.info("No se encontro en el destino:  %s vamos a crearlo.", nombre_o)

        try:
            return_id = sock_d.execute(
                dbname_d, uid_d, pwd_d, model_d, "create", valores_update
            )
            print("\033[92m", return_id, "EXITO AL CREAR", nombre_o, "\033[0m")
            logging.warning("%s, EXITO AL CREAR %s", return_id, nombre_o)
        except Exception as e:
            logging.error("================================================")
            logging.error(
                "Ha ocurrido un error al intentar crear el user: %s", nombre_o
            )
            logging.error(e)
            logging.error("================================================")
            ec += 1
        # print (registro_data_d)
        j += 1
logging.info("Cantidad de registros actualizados: %s", x)
logging.info("Cantidad de actualizados con error: %s", ea)
logging.info("Cantidad de registros creados: %s", j)
logging.info(" Cantidad de errores al crear: %s", ec)
