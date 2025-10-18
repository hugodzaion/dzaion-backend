import secrets

# Gera o diretório para salvar a foto
def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    random_name = secrets.token_hex(12)
    filename = f"{random_name}.{ext}"
    return f"user_{instance.id}/photos/{filename}"

