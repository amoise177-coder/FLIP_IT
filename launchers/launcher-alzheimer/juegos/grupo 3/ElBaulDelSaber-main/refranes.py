"""Catálogo terapéutico ordenado de menor a mayor dificultad."""
from models import Refran


def r(inicio, respuesta, significado, p1, p2, tema):
    return Refran(inicio, respuesta, significado, (p1, p2), tema)


REFRANES = [
    r("A quien madruga...", "Dios le ayuda.", "Empezar temprano puede abrir oportunidades.", "¿Quién decía este refrán?", "¿En qué momento del día lo escuchabas?", "Consejos"),
    r("Más vale tarde...", "que nunca.", "Es preferible hacer algo tarde que no hacerlo.", "¿Cuándo te animaste a hacer algo aunque fuera tarde?", "¿Con quién compartirías este dicho?", "Consejos"),
    r("Al mal tiempo...", "buena cara.", "Ante las dificultades, mantener una actitud serena ayuda.", "¿Quién te enseñó a ser optimista?", "¿Qué te ayuda en un día difícil?", "Consejos"),
    r("No por mucho madrugar...", "amanece más temprano.", "Hay cosas que necesitan su propio tiempo.", "¿Qué actividad hacías con paciencia?", "¿Qué recuerdo te trae la mañana?", "Consejos"),
    r("Camarón que se duerme...", "se lo lleva la corriente.", "Conviene estar atento a las oportunidades.", "¿Qué consejo recibías de pequeño?", "¿Qué te hace sentir despierto y activo?", "Consejos"),
    r("En casa de herrero...", "cuchillo de palo.", "A veces falta en casa lo que una persona sabe hacer.", "¿Qué oficio había en tu familia?", "¿Qué objeto especial recuerdas de tu casa?", "Familia"),
    r("Ojos que no ven...", "corazón que no siente.", "No saber algo puede evitar una preocupación.", "¿Qué canción te trae un recuerdo agradable?", "¿Quién te acompañaba en esos momentos?", "Amor"),
    r("El que busca...", "encuentra.", "La constancia ayuda a lograr lo que deseamos.", "¿Qué te gustaba buscar o coleccionar?", "¿Quién te ayudaba cuando lo necesitabas?", "Consejos"),
    r("Más vale pájaro en mano...", "que cien volando.", "Es mejor valorar lo seguro que arriesgarlo todo.", "¿Qué regalo sencillo atesoras?", "¿Qué decisión tomaste con prudencia?", "Consejos"),
    r("No dejes para mañana...", "lo que puedes hacer hoy.", "Hacer las tareas a tiempo evita preocupaciones.", "¿Qué rutina te gustaba mantener?", "¿Quién era muy organizado en tu familia?", "Trabajo"),
    r("El hábito no hace...", "al monje.", "La apariencia no define a las personas.", "¿Qué cualidad aprecias más en alguien?", "¿Quién te sorprendió por su forma de ser?", "Consejos"),
    r("Árbol que nace torcido...", "jamás su tronco endereza.", "Las costumbres tempranas pueden ser difíciles de cambiar.", "¿Qué costumbre familiar recuerdas?", "¿Qué aprendiste de tus mayores?", "Familia"),
    r("Barriga llena...", "corazón contento.", "Una buena comida puede traer bienestar y alegría.", "¿Qué comida te recuerda a tu familia?", "¿Quién la preparaba?", "Familia"),
    r("Dime con quién andas...", "y te diré quién eres.", "Las compañías influyen en nuestra vida.", "¿Quién fue un amigo importante para ti?", "¿Qué hacían juntos?", "Amistad"),
    r("No hay mal...", "que por bien no venga.", "De una dificultad puede nacer algo positivo.", "¿Qué aprendizaje te dejó un reto?", "¿Quién te apoyó entonces?", "Consejos"),
    r("El que ríe de último...", "ríe mejor.", "La paciencia puede dar buenos resultados.", "¿Qué situación te hizo reír mucho?", "¿Con quién te reías más?", "Amistad"),
    r("A caballo regalado...", "no se le mira el diente.", "Los regalos se agradecen sin exigir perfección.", "¿Cuál regalo recuerdas con cariño?", "¿Quién te lo dio?", "Familia"),
    r("Quien mucho abarca...", "poco aprieta.", "Es mejor concentrarse en una cosa a la vez.", "¿Qué actividad realizabas muy bien?", "¿Qué te gustaba terminar con calma?", "Trabajo"),
    r("La práctica hace...", "al maestro.", "Practicar permite aprender y mejorar.", "¿Qué aprendiste practicando?", "¿Quién fue tu maestro o guía?", "Trabajo"),
    r("El amor entra...", "por la cocina.", "Compartir comida también puede expresar cariño.", "¿Qué plato preparabas con amor?", "¿Para quién lo preparabas?", "Amor"),
    r("Donde hubo fuego...", "cenizas quedan.", "Los sentimientos o recuerdos intensos pueden permanecer.", "¿Qué lugar guarda un recuerdo especial?", "¿Qué te hace sentir nostalgia?", "Amor"),
    r("Cría cuervos...", "y te sacarán los ojos.", "A veces, cuidar sin límites puede traer decepciones.", "¿Qué consejo de crianza recuerdas?", "¿Qué valor enseñabas en casa?", "Familia"),
    r("Perro que ladra...", "no muerde.", "Quien amenaza mucho no siempre actúa.", "¿Tuviste una mascota especial?", "¿Cómo se llamaba?", "Familia"),
    r("El que mucho habla...", "mucho yerra.", "Hablar con prudencia ayuda a evitar equivocaciones.", "¿Quién hablaba mucho en las reuniones?", "¿Qué conversación recuerdas con cariño?", "Consejos"),
    r("La unión hace...", "la fuerza.", "Trabajar juntos permite conseguir más.", "¿Cuándo sentiste la fuerza de un grupo?", "¿Con quién te gustaba colaborar?", "Trabajo"),
    r("No hay rosa...", "sin espinas.", "Las cosas bellas también pueden tener dificultades.", "¿Qué flores recuerdas de tu hogar?", "¿Quién cuidaba el jardín?", "Amor"),
    r("Agua que no has de beber...", "déjala correr.", "Conviene no involucrarse en lo que no nos corresponde.", "¿Qué consejo te daban para vivir tranquilo?", "¿Quién era una persona sabia para ti?", "Consejos"),
    r("El que espera...", "desespera.", "Esperar puede resultar difícil cuando algo importa.", "¿Qué esperabas con ilusión de niño?", "¿Qué celebración familiar te emocionaba?", "Familia"),
    r("Cada cabeza...", "es un mundo.", "Cada persona tiene pensamientos y experiencias propias.", "¿Qué te hace único?", "¿Qué idea bonita heredaste de alguien?", "Consejos"),
    r("Quien siembra vientos...", "recoge tempestades.", "Nuestras acciones tienen consecuencias.", "¿Qué valor consideras importante?", "¿Qué enseñanza te dejó tu familia?", "Consejos"),
]
