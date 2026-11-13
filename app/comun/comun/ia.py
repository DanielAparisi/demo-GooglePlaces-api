"""Cliente de IA (Groq) compartido por scripts y backend."""
from groq import Groq

MODELO = 'llama-3.3-70b-versatile'

_cliente: Groq | None = None


def cliente() -> Groq:
    """Se crea al primer uso: importar este módulo no exige tener la clave."""
    global _cliente
    if _cliente is None:
        from comun.entorno import requerir
        try:
            clave = requerir('GROQ_API_KEY')
        except SystemExit as e:
            # `requerir` termina el proceso; aquí debe ser un error normal para que
            # quien llame pueda usar su plantilla de respaldo.
            raise RuntimeError(str(e)) from e
        _cliente = Groq(api_key=clave)
    return _cliente


def generar(prompt: str, *, temperature: float = 0.7, max_tokens: int = 500) -> str:
    resp = cliente().chat.completions.create(
        model=MODELO,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()
