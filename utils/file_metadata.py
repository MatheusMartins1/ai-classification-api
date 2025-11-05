# Custom serializer function
import os


def custom_serializer(obj):
    try:
        return str(obj)
    except TypeError:
        return None


def convert_size(size_in_bytes: int) -> str:
    """Converte tamanho em bytes para formato legível (KB, MB, GB)"""
    if size_in_bytes == 0:
        return ""

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_in_bytes)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.1f} {units[unit_index]}"


def get_file_type(filename: str) -> str:
    """Determina o tipo do arquivo baseado na extensão"""
    _, ext = os.path.splitext(filename.lower())
    return ext
