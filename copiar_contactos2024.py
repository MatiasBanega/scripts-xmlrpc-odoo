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
model_o = "res.partner"  # nombre del modelo de origen
model_d = "res.partner"  # nombre del modelo del destino
idant_o = "name"  # TO DO  generar el x_id_anterior nombre del campo a usar en el destino para almacenar id anterior, dejar vacio si no se usa. (tiene que ser un campo existente en el modelo model_d)
# este campo hay que crearlo en el modelo
campos = [
    "name",
    "function",
    "phone",
    "mobile",
    "email",
    "website",
    "title",
    "lang",
    "category_id",
    "company_type",
    "parent_id",
    "street",
    "street2",
    "city",
    "state_id",
    "zip",
    "country_id",
    "vat",
    "zona",
    "l10n_latam_identification_type_id",
    "l10n_ar_afip_responsibility_type_id",
    "id_sistema_la_red",
    "vendedor",
    "fechaultimacompra"
]
condi1_o = [('id', '>', '1')]

gcontext = ssl._create_unverified_context()

#########? ORIGEN
sock_common_o = xmlrpc.client.ServerProxy(
    web_o + 'xmlrpc/common' , context=gcontext
)
uid_o = sock_common_o.login(dbname_o, user_o, pwd_o)
#########?


#########? DESTINO
# Get the uid destino de los datos
sock_common_d = xmlrpc.client.ServerProxy(
    web_d + "xmlrpc/common", context=gcontext
)
uid_d = sock_common_d.login(dbname_d, user_d, pwd_d)
#########?

# reemplazar el valor de la ip o url del servidor de origen con su puerto
sock_o = xmlrpc.client.ServerProxy(
    web_o + "/xmlrpc/object", context=gcontext
)

# reemplazar el valor de la ip o url del servidor de destino con su puerto
sock_d = xmlrpc.client.ServerProxy(
    web_d + "xmlrpc/object", context=gcontext
)

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

registro_ids_o = sock_o.execute(dbname_o, uid_o, pwd_o, model_o, 'search', condi1_o)

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
    # vamos a usar el campo ref pero hay que usar en un futuro x_id_anterior de res.partner
    # si se econtro el registro se actualiza
    if registro_id_d:
        print(
            "Encontrado en el nuevo servidor",
            clave,
            "con nombre",
            nombre_o,
            "lo vamos a actualizar",
        )
        # aca nombramos variables para luego llamarlas dentro de valores_update, en especial las que devuelven un diccionario.
        valores_update = {
            "company_type": registro_data_o[0]['company_type'],
            "name": registro_data_o[0]['name'],
            "parent_id": registro_data_o[0]['parent_id'],
            "street": registro_data_o[0]['street'],
            "street2": registro_data_o[0]['street2'],
            "city": registro_data_o[0]['city'],
            "zip": registro_data_o[0]['zip'],
            "zona": registro_data_o[0]['zona'],
            "vat": registro_data_o[0]['vat'],
            "id_sistema_la_red": registro_data_o[0]['id_sistema_la_red'],
            "vendedor": registro_data_o[0]['vendedor'],
            "fechaultimacompra": registro_data_o[0]['fechaultimacompra'],
            "function": registro_data_o[0]['function'],
            "phone": registro_data_o[0]['phone'],
            "mobile": registro_data_o[0]['mobile'],
            "email": registro_data_o[0]['email'],
            "website": registro_data_o[0]['website'],
            "lang": registro_data_o[0]['lang'],
        }
        if registro_data_o[0]['state_id']:
            valores_update['state_id'] = registro_data_o[0]['state_id'][0]
        
        if registro_data_o[0]['country_id']:
            valores_update['country_id'] = registro_data_o[0]['country_id'][0]
        if registro_data_o[0]['l10n_latam_identification_type_id']:
            valores_update['l10n_latam_identification_type_id'] = registro_data_o[0]['l10n_latam_identification_type_id'][0]
        if registro_data_o[0]['l10n_ar_afip_responsibility_type_id']:
            valores_update['l10n_ar_afip_responsibility_type_id'] = registro_data_o[0]['l10n_ar_afip_responsibility_type_id'][0]
        # if registro_data_o[0]['category_id']:
        #     valores_update['category_id'] = registro_data_o[0]['category_id'][0]
        # if registro_data_o[0]['title']:
        #     valores_update = registro_data_o[0]['title'][0],


        # esta linea es la encargada de actualizar en el destino
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
        valores_update = {
            "id": registro_data_o[0]['id'],
            "company_type": registro_data_o[0]['company_type'],
            "name": registro_data_o[0]['name'],
            "parent_id": registro_data_o[0]['parent_id'],
            "street": registro_data_o[0]['street'],
            "street2": registro_data_o[0]['street2'],
            "city": registro_data_o[0]['city'],
            "zip": registro_data_o[0]['zip'],
            "zona": registro_data_o[0]['zona'],
            "vat": registro_data_o[0]['vat'],
            "id_sistema_la_red": registro_data_o[0]['id_sistema_la_red'],
            "vendedor": registro_data_o[0]['vendedor'],
            "fechaultimacompra": registro_data_o[0]['fechaultimacompra'],
            "function": registro_data_o[0]['function'],
            "phone": registro_data_o[0]['phone'],
            "mobile": registro_data_o[0]['mobile'],
            "email": registro_data_o[0]['email'],
            "website": registro_data_o[0]['website'],
            "lang": registro_data_o[0]['lang'],
        }
        if registro_data_o[0]['state_id']:
            valores_update['state_id'] = registro_data_o[0]['state_id'][0]
        
        if registro_data_o[0]['country_id']:
            valores_update['country_id'] = registro_data_o[0]['country_id'][0]
        if registro_data_o[0]['l10n_latam_identification_type_id']:
            valores_update['l10n_latam_identification_type_id'] = registro_data_o[0]['l10n_latam_identification_type_id'][0]
        if registro_data_o[0]['l10n_ar_afip_responsibility_type_id']:
            valores_update['l10n_ar_afip_responsibility_type_id'] = registro_data_o[0]['l10n_ar_afip_responsibility_type_id'][0]
        # if registro_data_o[0]['category_id']:
        #     valores_update['category_id'] = registro_data_o[0]['category_id'][0]
        # if registro_data_o[0]['title']:
        #     valores_update = registro_data_o[0]['title'][1]

        try:
            return_id = sock_d.execute(
                dbname_d, uid_d, pwd_d, model_d, "create", valores_update
            )
            print(return_id, "exito al crear ", nombre_o)
        except Exception as e:
            print("================================================")
            print("Ha ocurrido un error al intentar crear el user: ", nombre_o)
            print(e)
            ec += 1
        # print (registro_data_d)
        j += 1
print("Cantidad de registros actualizados: ", x)
print("Cantidad de actualizados con error: ", ea)
print("Cantidad de registros creados: ", j)
print(" Cantidad de errores al crear: ", ec)
