import sys
import xmlrpc.client
import ssl
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="copiar_productos_product.log",
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
model_o = "product.product"  # nombre del modelo de origen
model_d = "product.product"  # nombre del modelo del destino
idant_o = "name"  # TO DO  generar el x_id_anterior nombre del campo a usar en el destino para almacenar id anterior, dejar vacio si no se usa. (tiene que ser un campo existente en el modelo model_d)
# este campo hay que crearlo en el modelo
campos = [
    "name",
    "sale_ok",
    "detailed_type",
    "invoice_policy",
    "list_price",
    "taxes_id",
    "standard_price",
    "categ_id",
    "default_code",
    "barcode",
    "marca",
    "id_producto_cliente",
    "plu",
    "rubro",
    "alicuotaiva",
    "categoria",
    "fechaultimacompra",
    "descuento",
    "clasificacion",
    "problema",
    "tipo_producto",
    "description",
    "weight",
    "volume",
    "sale_delay",
    "width",
    "height",
    "preciodeventa2",
    "preciodeventa3",
    "preciosugerido",
    "preciomodificable",
    "descuento2",
    "descuento3",
    "proveedor",
    "cantidadbulto",
    "descuentocompra1",
    "descuentocompra2",
    "descuentocompra3",
    "descuentocompra4",
    "rentabilidad1",
    "rentabilidad2",
    "rentabilidad3",
    "puntominimo1",
    "puntominimo2",
    "puntominimo3",
    "puntominimo4",
    "puntominimo5",
    "puntominimo6",
    "tracking",
]
condi1_o = [("list_price", ">", "0")]

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

registro_ids_o = sock_o.execute(
    dbname_o, uid_o, pwd_o, "product.template", "search", condi1_o
)

# Iniciar los contadores
x = 0
j = 0
ec = 0
ea = 0

for i in registro_ids_o:
    # if j == 100:
    #     break
    # Leemos la info de los registros en la base origen

    registro_data_o = sock_o.execute(
        dbname_o, uid_o, pwd_o, "product.template", "read", i, campos
    )
    # obteniendo la ID original para buscar en el destino
    if registro_data_o:
        logging.info(
            "cada registro de origen lo llamamos i, contiene lo siguiente: %s", i
        )
        logging.info(
            "Verificando en el origen el modelo:  %s,  el objeto con id:  %s",
            model_o,
            i,
        )
        logging.info("Registro  Obtenido: %s", registro_data_o)
        clave = registro_data_o[0]["id"]
        nombre_o = registro_data_o[0]["name"]
    else:
        continue
    # Busqueda por id_anterior en el destino para ver si existe y se actualiza o hay que crearlo.
    # si el ODOO DE DESTINO tiene mas campos requeridos puede fallar, pero se agregan en la variable campos.
    # conviene importar antes de seguir instalando muchos modulos.
    # BUSCAMOS EN EL DESTINO SI EXISTE un res.users con el valor de idant_o (tiene que existir ente valor en el modelo) igual a clave
    # registro_id_d = sock_d.execute(
    #     dbname_d, uid_d, pwd_d, model_d, "search", [("plu", "=", registro_data_o[0]["plu"])]
    # )
    product_tmpl_id = sock_d.execute(
        dbname_d,
        uid_d,
        pwd_d,
        "product.template",
        "search",
        [("plu", "=", registro_data_o[0]["plu"])],
    )
    # vamos a usar el campo ref pero hay que usar en un futuro x_id_anterior de res.partner
    # si se econtro el registro se actualiza
    if product_tmpl_id:
        logging.info(
            "Encontrado en el nuevo servidor %s con nombre %s lo vamos a actualizar",
            clave,
            nombre_o,
        )

        # aca nombramos variables para luego llamarlas dentro de valores_update, en especial las que devuelven un diccionario.
        valores_update = {
            # "id": registro_data_o[0]["id"],
            "name": registro_data_o[0]["name"],
            "sale_ok": registro_data_o[0]["sale_ok"],
            "detailed_type": registro_data_o[0]["detailed_type"],
            "list_price": registro_data_o[0]["list_price"],
            "standard_price": registro_data_o[0]["standard_price"],
            "default_code": registro_data_o[0]["default_code"],
            "barcode": registro_data_o[0]["barcode"],
            "marca": registro_data_o[0]["marca"],
            "id_producto_cliente": registro_data_o[0]["id_producto_cliente"],
            "plu": registro_data_o[0]["plu"],
            "rubro": registro_data_o[0]["rubro"],
            "alicuotaiva": registro_data_o[0]["alicuotaiva"],
            "categoria": registro_data_o[0]["categoria"],
            "fechaultimacompra": registro_data_o[0]["fechaultimacompra"],
            "descuento": registro_data_o[0]["descuento"],
            "clasificacion": registro_data_o[0]["clasificacion"],
            "problema": registro_data_o[0]["problema"],
            "tipo_producto": registro_data_o[0]["tipo_producto"],
            "description": registro_data_o[0]["description"],
            "weight": registro_data_o[0]["weight"],
            "volume": registro_data_o[0]["volume"],
            "sale_delay": registro_data_o[0]["sale_delay"],
            "width": registro_data_o[0]["width"],
            "height": registro_data_o[0]["height"],
            "preciodeventa2": registro_data_o[0]["preciodeventa2"],
            "preciodeventa3": registro_data_o[0]["preciodeventa3"],
            "preciosugerido": registro_data_o[0]["preciosugerido"],
            "descuento2": registro_data_o[0]["descuento2"],
            "descuento3": registro_data_o[0]["descuento3"],
            "proveedor": registro_data_o[0]["proveedor"],
            "cantidadbulto": registro_data_o[0]["cantidadbulto"],
            "descuentocompra1": registro_data_o[0]["descuentocompra1"],
            "descuentocompra2": registro_data_o[0]["descuentocompra2"],
            "descuentocompra3": registro_data_o[0]["descuentocompra3"],
            "descuentocompra4": registro_data_o[0]["descuentocompra4"],
            "rentabilidad1": registro_data_o[0]["rentabilidad1"],
            "rentabilidad2": registro_data_o[0]["rentabilidad2"],
            "rentabilidad3": registro_data_o[0]["rentabilidad3"],
            "puntominimo1": registro_data_o[0]["puntominimo1"],
            "puntominimo2": registro_data_o[0]["puntominimo2"],
            "puntominimo3": registro_data_o[0]["puntominimo3"],
            "puntominimo4": registro_data_o[0]["puntominimo4"],
            "puntominimo5": registro_data_o[0]["puntominimo5"],
            "puntominimo6": registro_data_o[0]["puntominimo6"],
            "tracking": registro_data_o[0]["tracking"],
        }

        # if registro_data_o[0]["categ_id"]:
        #   valores_update["categ_id"] = registro_data_o[0]["categ_id"][0]
        # # if registro_data_o[0]["taxes_id"]:
        # #   valores_update["taxes_id"] = registro_data_o[0]["taxes_id"][0]
        # if registro_data_o[0]["invoice_policy"] == 1:
        #     valores_update["invoice_policy"] = ''
        # valores_update={"plu": registro_data_o[0]["plu"], "marca": registro_data_o[0]["marca"]}
        try:
            return_id = sock_d.execute(
                dbname_d,
                uid_d,
                pwd_d,
                model_d,
                "write",
                product_tmpl_id,
                valores_update,
            )
            logging.info("================================================")
            logging.info("%s, EXITO AL ACTUALIZAR %s", return_id, nombre_o)
            logging.info("================================================")
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
    # else:
    #     print("No se encontro en el destino: ", nombre_o, " vamos a crearlo.")
    #     valores_update = {
    #         "id": registro_data_o[0]["id"],
    #         "name": registro_data_o[0]["name"],
    #         "sale_ok": registro_data_o[0]["sale_ok"],
    #         "detailed_type": registro_data_o[0]["detailed_type"],
    #         "list_price": registro_data_o[0]["list_price"],
    #         "standard_price": registro_data_o[0]["standard_price"],
    #         "default_code": registro_data_o[0]["default_code"],
    #         "barcode": registro_data_o[0]["barcode"],
    #         "marca": registro_data_o[0]["marca"],
    #         "id_producto_cliente": registro_data_o[0]["id_producto_cliente"],
    #         "plu": registro_data_o[0]["plu"],
    #         "rubro": registro_data_o[0]["rubro"],
    #         "alicuotaiva": registro_data_o[0]["alicuotaiva"],
    #         "categoria": registro_data_o[0]["categoria"],
    #         "fechaultimacompra": registro_data_o[0]["fechaultimacompra"],
    #         "descuento": registro_data_o[0]["descuento"],
    #         "clasificacion": registro_data_o[0]["clasificacion"],
    #         "problema": registro_data_o[0]["problema"],
    #         "tipo_producto": registro_data_o[0]["tipo_producto"],
    #         "description": registro_data_o[0]["description"],
    #         "weight": registro_data_o[0]["weight"],
    #         "volume": registro_data_o[0]["volume"],
    #         "sale_delay": registro_data_o[0]["sale_delay"],
    #         "width": registro_data_o[0]["width"],
    #         "height": registro_data_o[0]["height"],
    #         "preciodeventa2": registro_data_o[0]["preciodeventa2"],
    #         "preciodeventa3": registro_data_o[0]["preciodeventa3"],
    #         "preciosugerido": registro_data_o[0]["preciosugerido"],
    #         "descuento2": registro_data_o[0]["descuento2"],
    #         "descuento3": registro_data_o[0]["descuento3"],
    #         "proveedor": registro_data_o[0]["proveedor"],
    #         "cantidadbulto": registro_data_o[0]["cantidadbulto"],
    #         "descuentocompra1": registro_data_o[0]["descuentocompra1"],
    #         "descuentocompra2": registro_data_o[0]["descuentocompra2"],
    #         "descuentocompra3": registro_data_o[0]["descuentocompra3"],
    #         "descuentocompra4": registro_data_o[0]["descuentocompra4"],
    #         "rentabilidad1": registro_data_o[0]["rentabilidad1"],
    #         "rentabilidad2": registro_data_o[0]["rentabilidad2"],
    #         "rentabilidad3": registro_data_o[0]["rentabilidad3"],
    #         "puntominimo1": registro_data_o[0]["puntominimo1"],
    #         "puntominimo2": registro_data_o[0]["puntominimo2"],
    #         "puntominimo3": registro_data_o[0]["puntominimo3"],
    #         "puntominimo4": registro_data_o[0]["puntominimo4"],
    #         "puntominimo5": registro_data_o[0]["puntominimo5"],
    #         "puntominimo6": registro_data_o[0]["puntominimo6"],
    #         "tracking": registro_data_o[0]["tracking"]
    #     }

    #     if registro_data_o[0]["categ_id"]:
    #       valores_update["categ_id"] = registro_data_o[0]["categ_id"][0]

    #     if registro_data_o[0]["invoice_policy"] == 1:
    #         valores_update["invoice_policy"] = ''
    #     if product_tmpl_id:
    #         valores_update["product_tmpl_id"] = product_tmpl_id
    #     # if registro_data_o[0]["taxes_id"]:
    #     #   valores_update["taxes_id"] = registro_data_o[0]["taxes_id"][0]

    #     try:
    #         return_id = sock_d.execute(
    #             dbname_d, uid_d, pwd_d, model_d, "create", valores_update
    #         )
    #         print(return_id, "\033[92mEXITO AL CREAR\033[0m ", nombre_o)
    #     except Exception as e:
    #         print("\033[91m================================================\033[0m")
    #         print("\033[91mHa ocurrido un error al intentar crear el user: ", nombre_o, "\033[0m")
    #         print("\033",e,"\033[0m")
    #         print("\033[91m================================================\033[0m")
    #         break

    #         ec += 1
    #     # print (registro_data_d)
    #     j += 1
logging.info("Cantidad de registros actualizados: %s", x)
logging.info("Cantidad de actualizados con error: %s", ea)
logging.info("Cantidad de registros creados: %s", j)
logging.info(" Cantidad de errores al crear: %s", ec)
