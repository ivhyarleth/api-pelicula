import json
import boto3
import uuid

def lambda_handler(event, context):
    # Para imprimir SIEMPRE un json válido:
    def log_info(datos):
        log = {
            "tipo": "INFO",
            "log_datos": datos
        }
        print(json.dumps(log, ensure_ascii=False))

    def log_error(datos):
        log = {
            "tipo": "ERROR",
            "log_datos": datos
        }
        print(json.dumps(log, ensure_ascii=False))

    try:
        # 1. Leer body del evento
        body = json.loads(event["body"])
        tenant_id = body["tenant_id"]               # ej. "CINEPLANET"
        pelicula = body["pelicula_datos"]           # dict con nombre, genero, fecha, etc.

        # 2. Preparar item para DynamoDB
        pelicula_id = str(uuid.uuid4())
        item = {
            "uuid": pelicula_id,
            "tenant_id": tenant_id,
            "pelicula_datos": pelicula
        }

        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table("NOMBRE_TABLA_PELICULA")  # pon aquí tu tabla real

        response = table.put_item(Item=item)

        # 3. LOG de éxito (INFO)
        log_info({
            "tenant_id": tenant_id,
            "pelicula_datos": pelicula,
            "operacion": "crear_pelicula",
            "detalle": "Película creada correctamente",
            "request_id": context.aws_request_id
        })

        # 4. Respuesta HTTP correcta
        return {
            "statusCode": 200,
            "body": json.dumps({
                "mensaje": "Película creada correctamente",
                "uuid": pelicula_id
            }, ensure_ascii=False)
        }

    except Exception as e:
        # 5. LOG de error (ERROR)
        log_error({
            "mensaje_error": str(e),
            "event_raw": event,  # opcional: para depurar
            "operacion": "crear_pelicula",
            "request_id": context.aws_request_id
        })

        # 6. Respuesta HTTP de error
        return {
            "statusCode": 500,
            "body": json.dumps({
                "mensaje": "Error al crear la película",
                "error": str(e)
            }, ensure_ascii=False)
        }
