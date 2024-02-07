import sys
import xmlrpc.client
import ssl


user_o = "Nelsonjr"  # el usuario de odoo origen
pwd_o = "Nelsonjr"  # contrasenia de usuario odoo origen

user_d = "Nelsonjr"  # el usuario de odoo destino
pwd_d = "Nelsonjr"  # contrasenia de usuario destino

dbname_o = "lared.devman.com.ar"  # nombre de base de datos origen
dbname_d = "lared-rma-test.devman.com.ar"  # nombre de base de datos destino

web_o = "https://lared.devman.com.ar/"  # ip o dir web del origen
web_d = "https://lared-rma-test.devman.com.ar/"  # ip o dir web del destino
# datos de los modelos y campos
model_o = "rma_seminuevos"  # nombre del modelo de origen
model_d = "rma_seminuevos"  # nombre del modelo del destino
idant_o = "name"  # TO DO  generar el x_id_anterior nombre del campo a usar en el destino para almacenar id anterior, dejar vacio si no se usa. (tiene que ser un campo existente en el modelo model_d)
# este campo hay que crearlo en el modelo
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

# reemplazar el valor de la ip o url del servidor de origen con su puerto
sock_o = xmlrpc.client.ServerProxy(web_o + "/xmlrpc/object", context=gcontext)

# reemplazar el valor de la ip o url del servidor de destino con su puerto
sock_d = xmlrpc.client.ServerProxy(web_d + "xmlrpc/object", context=gcontext)

print("===========================================")
print("Se van a importar los siguientes registros:")
print("Web de origen..: ", web_o)
print("Modelo a migrar: ", model_o)
print("-------------------------------------------")
print("Se van a actualizar/crear los siguientes registros:")
print("Web de destino.: ", web_d)
print("Modelo migrado.: ", model_d)
print("Campo id anter.: ", idant_o)
print("===========================================")

registro_ids_o = sock_o.execute(dbname_o, uid_o, pwd_o, model_o, "search", condi1_o)

# Iniciar los contadores
x = 0
j = 0
ec = 0
ea = 0

for i in registro_ids_o:
    # Leemos la info de los registros en la base origen
    print(" cada registro de origen lo llamamos i, contiene lo siguiente: ", i)
    print("Verificando en el origen el modelo: ", model_o, " el objeto con id: ", i)
    registro_data_o = sock_o.execute(dbname_o, uid_o, pwd_o, model_o, "read", i, campos)
    print("Registro  Obtenido: ", registro_data_o)
    # obteniendo la ID original para buscar en el destino
    clave = registro_data_o[0]["id"]
    nombre_o = registro_data_o[0]["name"]
    # Busqueda por id_anterior en el destino para ver si existe y se actualiza o hay que crearlo.
    # si el ODOO DE DESTINO tiene mas campos requeridos puede fallar, pero se agregan en la variable campos.
    # conviene importar antes de seguir instalando muchos modulos.
    # BUSCAMOS EN EL DESTINO SI EXISTE un res.users con el valor de idant_o (tiene que existir ente valor en el modelo) igual a clave
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
    # vamos a usar el campo ref pero hay que usar en un futuro x_id_anterior de res.partner
    # si se econtro el registro se actualiza
    valores_update = {
        "name": registro_data_o[0]["name"],
        "falla_aparente": registro_data_o[0]["falla_aparente"],
        "stock_lot": registro_data_o[0]["stock_lot"],
        "estado": registro_data_o[0]["estado"],
        "fecha_carga": registro_data_o[0]["fecha_carga"],
        "create_uid": registro_data_o[0]["create_uid"],
        "marca": registro_data_o[0]["marca"],
        "plu": registro_data_o[0]["plu"],
        "fecha_mod_estado": registro_data_o[0]["fecha_mod_estado"],
        "proveedor": registro_data_o[0]["proveedor"],
        "orden_service": registro_data_o[0]["orden_service"],
        "fecha_ingreso": registro_data_o[0]["fecha_ingreso"],
        "fecha_retiro": registro_data_o[0]["fecha_retiro"],
        "detalle": registro_data_o[0]["detalle"],
        "costo": registro_data_o[0]["costo"],
        "estado_service": registro_data_o[0]["estado_service"],
    }
    if product_id_destino:
        valores_update["productos_id"] = product_id_destino[0]

    if registro_id_d:
        print(
            "Encontrado en el nuevo servidor",
            clave,
            "con nombre",
            nombre_o,
            "lo vamos a actualizar",
        )
        # aca nombramos variables para luego llamarlas dentro de valores_update, en especial las que devuelven un diccionario.

        try:
            return_id = sock_d.execute(
                dbname_d, uid_d, pwd_d, model_d, "write", registro_id_d, valores_update
            )
            print(return_id, "exito al actualizar user ", nombre_o)
        except Exception as e:
            print("Ha ocurrido un error al intentar actualizar el user: ", nombre_o)
            print(e)
            ea += 1
        x += 1
    # si no se econtro el registro en el destino se crea
    else:
        print("No se encontro en el destino: ", nombre_o, " vamos a crearlo.")

        try:
            return_id = sock_d.execute(
                dbname_d, uid_d, pwd_d, model_d, "create", valores_update
            )
            print(return_id, "========= exito al crear =========", nombre_o)
        except Exception as e:
            print("================================================")
            print("Ha ocurrido un error al intentar crear el user: ", nombre_o)
            print(e)
            print("================================================")
            ec += 1
        # print (registro_data_d)
        j += 1
print("Cantidad de registros actualizados: ", x)
print("Cantidad de actualizados con error: ", ea)
print("Cantidad de registros creados: ", j)
print(" Cantidad de errores al crear: ", ec)
