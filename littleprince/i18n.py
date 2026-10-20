"""Coklu dil destegi (20 dil).

Replikler, Saint-Exupery'nin FRANSIZCA ozgun metnine dayanir.
Ingilizce'de klasik Katherine Woods cevirisinin yaygin ifadeleri kullanilir;
diger dillerde anlam korunarak yapilmis ceviriler yer alir. Yayinevleri
kucuk kelime farkliliklari kullanabilir.
"""
from __future__ import annotations

import re

# Hangi turun hangi repligi YOLDASIN kendi agzindan soylenir.
# (index: o turun listesindeki sira; None = o tur konusmaz)
SAID_INDEX = {
    "fox": 0,          # "Tilki: Evcilleştir beni!" -> tilki soyler
    "rose": None,      # gul konusmaz, hepsi Prens'in sozu
    "lamplighter": 0,  # fenercinin kendi repligi
    "snake": 0,        # yilanin kendi repligi
    "baobab": None,    # agac konusmaz
}

_QUOTED = re.compile(r'[:：]\s*[“"«„「]\s*(.+?)\s*[”"»“」]')


def _strip_quotes(line: str) -> str:
    """'Tilki: “Evcilleştir beni!”' -> 'Evcilleştir beni!'"""
    match = _QUOTED.search(line or "")
    return match.group(1).strip() if match else (line or "").strip()

LANGS = [
    ("auto", "Automatic (system language)"),
    ("en", "English"),
    ("tr", "Türkçe"),
    ("es", "Español"),
    ("fr", "Français"),
    ("de", "Deutsch"),
    ("it", "Italiano"),
    ("pt", "Português"),
    ("nl", "Nederlands"),
    ("pl", "Polski"),
    ("ru", "Русский"),
    ("uk", "Українська"),
    ("zh", "中文"),
    ("ja", "日本語"),
    ("ko", "한국어"),
    ("hi", "हिन्दी"),
    ("bn", "বাংলা"),
    ("ar", "العربية"),
    ("fa", "فارسی"),
    ("id", "Bahasa Indonesia"),
    ("vi", "Tiếng Việt"),
]

CODES = [code for code, _ in LANGS if code != "auto"]

STRINGS: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# ENGLISH
# ---------------------------------------------------------------------------
STRINGS["en"] = {
    "quotes": [
        "Hello! I am the Little Prince.",
        "Have you seen my rose?",
        "The stars are a million little bells.",
        "It is only with the heart that one can see rightly; what is essential is invisible to the eye.",
        "Please—tame me!",
        "Grown-ups never understand anything by themselves, and children are forever explaining things to them.",
        "What makes the desert beautiful is that somewhere it hides a well.",
        "My rose… I am responsible for her.",
        "One runs the risk of weeping a little, if one lets oneself be tamed.",
        "It is the time you have wasted for your rose that makes your rose so important.",
    ],
    "fox": ["The fox: “Tame me!”", "The fox came. Now we need each other."],
    "rose": ["My rose is here. I am responsible for her.", "My rose… mind her thorns!"],
    "lamplighter": [
        "The lamplighter: “Good day, good evening!”",
        "He lights and puts out his lamp every minute.",
    ],
    "snake": ["The snake: “You are lonely among people.”", "The snake is here. Let us not move."],
    "baobab": ["A baobab! Pull it out before it splits the planet.", "Baobab seeds are dangerous. Careful!"],
    "wake": ["Hmm? I fell asleep…", "Good morning! Was I counting stars?", "Oh, it's you!"],
    "land": ["Ouch!", "That was too high…", "Oof!"],
    "menu": {
        "sit": "Sit down",
        "stand": "Get up",
        "wake": "Wake up",
        "chat": "Talk (AI)…",
        "quote": "Say a line from the book",
        "walk": "Start wandering",
        "teleport": "Teleport",
        "settings": "Settings…",
        "respawn": "Bring to screen",
        "quit": "Quit",
    },
    "no_surface": "There is no other surface nearby…",
}

# ---------------------------------------------------------------------------
# TURKCE
# ---------------------------------------------------------------------------
STRINGS["tr"] = {
    "quotes": [
        "Merhaba! Ben Küçük Prens.",
        "Gülümü gördün mü?",
        "Yıldızlar, çiçek açan milyonlarca çan gibidir.",
        "İnsan ancak yüreğiyle bakarsa doğruyu görebilir. En önemli şey gözle görülmez.",
        "Evcilleştir beni!",
        "Büyükler hiçbir şeyi tek başlarına anlayamazlar.",
        "Çölü güzelleştiren, bir yerlerde bir kuyu saklamasıdır.",
        "Gülüm… ondan sorumluyum ben.",
        "Bir kere evcilleştirdin mi, artık ağlamak kaçınılmaz olur.",
        "Gülünü bu kadar değerli yapan, onun için harcadığın zamandır.",
    ],
    "fox": ["Tilki: “Evcilleştir beni!”", "Tilki geldi. Artık birbirimize ihtiyacımız var."],
    "rose": ["Gülüm geldi. Ondan sorumluyum ben.", "Gülüm… dikenlerine dikkat!"],
    "lamplighter": [
        "Fenerci: “Emredersiniz! İyi günler, iyi akşamlar!”",
        "Fenerci her dakika fenerini yakıp söndürüyor.",
    ],
    "snake": ["Yılan: “İnsanlar arasına düştüğün günden beri yalnızsın.”", "Yılan geldi. Kıpırdamayalım."],
    "baobab": ["Baobap! Zamanında sökmezsen gezegeni yarar.", "Baobap tohumları tehlikeli; dikkatli olmalıyım."],
    "wake": ["Hmm? Uyuyakalmışım…", "Günaydın! Yıldızları mı sayıyordum?", "Aa, sen mi geldin?"],
    "land": ["Aaa!", "Bu kadar yüksek olmasaydı iyi olurdu…", "Uf!"],
    "menu": {
        "sit": "Otur",
        "stand": "Kalk",
        "wake": "Uyandır",
        "chat": "Konuş (yapay zekâ)…",
        "quote": "Kitaptan bir söz söyle",
        "walk": "Gezinmeye başla",
        "teleport": "Işınlan",
        "settings": "Ayarlar…",
        "respawn": "Ekrana getir",
        "quit": "Çıkış",
    },
    "no_surface": "Yakında başka bir yüzey yok ki…",
}

# ---------------------------------------------------------------------------
# ESPANOL
# ---------------------------------------------------------------------------
STRINGS["es"] = {
    "quotes": [
        "¡Hola! Soy el Principito.",
        "¿Has visto mi rosa?",
        "Las estrellas son un millón de campanillas.",
        "Solo se ve bien con el corazón. Lo esencial es invisible a los ojos.",
        "¡Domestícame, por favor!",
        "Los mayores nunca comprenden nada por sí solos.",
        "Lo que hace bello al desierto es que esconde un pozo en algún lugar.",
        "Mi rosa… yo soy responsable de ella.",
        "Cuando domesticas a alguien, ya te expones a llorar un poco.",
        "Es el tiempo que perdiste por tu rosa lo que hace que sea tan importante.",
    ],
    "fox": ["El zorro: «¡Domestícame!»", "Llegó el zorro. Ahora nos necesitamos."],
    "rose": ["Mi rosa está aquí. Soy responsable de ella.", "Mi rosa… ¡cuidado con sus espinas!"],
    "lamplighter": [
        "El farolero: «¡Buenos días, buenas noches!»",
        "Enciende y apaga su farol cada minuto.",
    ],
    "snake": ["La serpiente: «Estás solo entre los hombres.»", "Llegó la serpiente. No nos movamos."],
    "baobab": ["¡Un baobab! Arráncalo antes de que rompa el planeta.", "Las semillas de baobab son peligrosas. ¡Cuidado!"],
    "wake": ["¿Mmm? Me quedé dormido…", "¡Buenos días! ¿Estaba contando estrellas?", "¡Ah, eres tú!"],
    "land": ["¡Ay!", "Eso fue demasiado alto…", "¡Uf!"],
    "menu": {
        "sit": "Sentarse",
        "stand": "Levantarse",
        "wake": "Despertar",
        "chat": "Hablar (IA)…",
        "quote": "Decir una frase del libro",
        "walk": "Empezar a pasear",
        "teleport": "Teletransportarse",
        "settings": "Ajustes…",
        "respawn": "Traer a la pantalla",
        "quit": "Salir",
    },
    "no_surface": "No hay otra superficie cerca…",
}

# ---------------------------------------------------------------------------
# FRANCAIS
# ---------------------------------------------------------------------------
STRINGS["fr"] = {
    "quotes": [
        "Bonjour ! Je suis le Petit Prince.",
        "As-tu vu ma rose ?",
        "Les étoiles sont un million de petites clochettes.",
        "On ne voit bien qu'avec le cœur. L'essentiel est invisible pour les yeux.",
        "Apprivoise-moi, s'il te plaît !",
        "Les grandes personnes ne comprennent jamais rien toutes seules.",
        "Ce qui embellit le désert, c'est qu'il cache un puits quelque part.",
        "Ma rose… je suis responsable d'elle.",
        "Quand on a apprivoisé quelqu'un, on risque de pleurer un peu.",
        "C'est le temps que tu as perdu pour ta rose qui la rend si importante.",
    ],
    "fox": ["Le renard : « Apprivoise-moi ! »", "Le renard est venu. Maintenant nous avons besoin l'un de l'autre."],
    "rose": ["Ma rose est là. Je suis responsable d'elle.", "Ma rose… attention à ses épines !"],
    "lamplighter": [
        "L'allumeur de réverbères : « Bonjour, bonsoir ! »",
        "Il allume et éteint sa lanterne chaque minute.",
    ],
    "snake": ["Le serpent : « Tu es bien seul parmi les hommes. »", "Le serpent est là. Ne bougeons pas."],
    "baobab": ["Un baobab ! Arrache-le avant qu'il ne fende la planète.", "Les graines de baobab sont dangereuses. Attention !"],
    "wake": ["Hein ? Je me suis endormi…", "Bonjour ! Je comptais les étoiles ?", "Ah, c'est toi !"],
    "land": ["Aïe !", "C'était trop haut…", "Ouf !"],
    "menu": {
        "sit": "S'asseoir",
        "stand": "Se lever",
        "wake": "Réveiller",
        "chat": "Parler (IA)…",
        "quote": "Dire une phrase du livre",
        "walk": "Partir se promener",
        "teleport": "Se téléporter",
        "settings": "Réglages…",
        "respawn": "Ramener à l'écran",
        "quit": "Quitter",
    },
    "no_surface": "Il n'y a pas d'autre surface près d'ici…",
}

# ---------------------------------------------------------------------------
# DEUTSCH
# ---------------------------------------------------------------------------
STRINGS["de"] = {
    "quotes": [
        "Hallo! Ich bin der kleine Prinz.",
        "Hast du meine Rose gesehen?",
        "Die Sterne sind eine Million kleine Glocken.",
        "Man sieht nur mit dem Herzen gut. Das Wesentliche ist für die Augen unsichtbar.",
        "Bitte… zähme mich!",
        "Die Erwachsenen verstehen nie etwas von selbst.",
        "Was die Wüste schön macht, ist, dass sie irgendwo einen Brunnen verbirgt.",
        "Meine Rose… ich bin für sie verantwortlich.",
        "Wenn du jemanden gezähmt hast, musst du damit rechnen, ein wenig zu weinen.",
        "Die Zeit, die du für deine Rose verloren hast, macht sie so wichtig.",
    ],
    "fox": ["Der Fuchs: „Zähme mich!“", "Der Fuchs ist da. Jetzt brauchen wir einander."],
    "rose": ["Meine Rose ist da. Ich bin für sie verantwortlich.", "Meine Rose… pass auf ihre Dornen auf!"],
    "lamplighter": [
        "Der Laternenanzünder: „Guten Tag, guten Abend!“",
        "Er zündet jede Minute seine Laterne an und löscht sie.",
    ],
    "snake": ["Die Schlange: „Du bist einsam unter den Menschen.“", "Die Schlange ist da. Bewegen wir uns nicht."],
    "baobab": ["Ein Baobab! Reiß ihn aus, bevor er den Planeten sprengt.", "Baobabsamen sind gefährlich. Vorsicht!"],
    "wake": ["Hm? Ich bin eingeschlafen…", "Guten Morgen! Habe ich Sterne gezählt?", "Oh, du bist es!"],
    "land": ["Au!", "Das war zu hoch…", "Uff!"],
    "menu": {
        "sit": "Hinsetzen",
        "stand": "Aufstehen",
        "wake": "Aufwecken",
        "chat": "Sprechen (KI)…",
        "quote": "Einen Satz aus dem Buch sagen",
        "walk": "Spazieren gehen",
        "teleport": "Teleportieren",
        "settings": "Einstellungen…",
        "respawn": "Auf den Bildschirm holen",
        "quit": "Beenden",
    },
    "no_surface": "Hier ist keine andere Fläche in der Nähe…",
}

# ---------------------------------------------------------------------------
# ITALIANO
# ---------------------------------------------------------------------------
STRINGS["it"] = {
    "quotes": [
        "Ciao! Sono il Piccolo Principe.",
        "Hai visto la mia rosa?",
        "Le stelle sono un milione di campanelli.",
        "Non si vede bene che col cuore. L'essenziale è invisibile agli occhi.",
        "Addomesticami, ti prego!",
        "I grandi non capiscono mai niente da soli.",
        "Ciò che rende bello il deserto è che nasconde un pozzo da qualche parte.",
        "La mia rosa… sono responsabile di lei.",
        "Quando hai addomesticato qualcuno, piangi un po', inevitabilmente.",
        "È il tempo che hai perduto per la tua rosa che la rende così importante.",
    ],
    "fox": ["La volpe: «Addomesticami!»", "È arrivata la volpe. Ora abbiamo bisogno l'uno dell'altra."],
    "rose": ["La mia rosa è qui. Sono responsabile di lei.", "La mia rosa… attenzione alle spine!"],
    "lamplighter": [
        "Il lampionaio: «Buongiorno, buonasera!»",
        "Accende e spegne il lampione ogni minuto.",
    ],
    "snake": ["Il serpente: «Sei solo in mezzo agli uomini.»", "È arrivato il serpente. Non muoviamoci."],
    "baobab": ["Un baobab! Strappalo prima che spacchi il pianeta.", "I semi di baobab sono pericolosi. Attento!"],
    "wake": ["Mmmh? Mi sono addormentato…", "Buongiorno! Stavo contando le stelle?", "Ah, sei tu!"],
    "land": ["Ahia!", "Era troppo alto…", "Uff!"],
    "menu": {
        "sit": "Siediti",
        "stand": "Alzati",
        "wake": "Sveglia",
        "chat": "Parla (IA)…",
        "quote": "Di' una frase dal libro",
        "walk": "Inizia a girare",
        "teleport": "Teletrasportati",
        "settings": "Impostazioni…",
        "respawn": "Porta sullo schermo",
        "quit": "Esci",
    },
    "no_surface": "Non c'è un'altra superficie qui vicino…",
}

# ---------------------------------------------------------------------------
# PORTUGUES
# ---------------------------------------------------------------------------
STRINGS["pt"] = {
    "quotes": [
        "Olá! Eu sou o Pequeno Príncipe.",
        "Você viu a minha rosa?",
        "As estrelas são um milhão de sininhos.",
        "Só se vê bem com o coração. O essencial é invisível aos olhos.",
        "Cativa-me, por favor!",
        "Os adultos nunca entendem nada sozinhos.",
        "O que torna o deserto belo é que ele esconde um poço em algum lugar.",
        "Minha rosa… eu sou responsável por ela.",
        "Depois de cativar alguém, a gente chora um pouco, inevitavelmente.",
        "É o tempo que você perdeu com a sua rosa que a torna tão importante.",
    ],
    "fox": ["A raposa: «Cativa-me!»", "A raposa chegou. Agora precisamos um do outro."],
    "rose": ["Minha rosa está aqui. Sou responsável por ela.", "Minha rosa… cuidado com os espinhos!"],
    "lamplighter": [
        "O acendedor: «Bom dia, boa noite!»",
        "Ele acende e apaga o lampião a cada minuto.",
    ],
    "snake": ["A serpente: «Você é solitário entre os homens.»", "A serpente chegou. Não nos mexamos."],
    "baobab": ["Um baobá! Arranque-o antes que rache o planeta.", "Sementes de baobá são perigosas. Cuidado!"],
    "wake": ["Hmm? Eu adormeci…", "Bom dia! Eu estava contando estrelas?", "Ah, é você!"],
    "land": ["Ai!", "Era alto demais…", "Ufa!"],
    "menu": {
        "sit": "Sentar",
        "stand": "Levantar",
        "wake": "Acordar",
        "chat": "Conversar (IA)…",
        "quote": "Dizer uma frase do livro",
        "walk": "Começar a passear",
        "teleport": "Teletransportar",
        "settings": "Configurações…",
        "respawn": "Trazer para a tela",
        "quit": "Sair",
    },
    "no_surface": "Não há outra superfície por perto…",
}

# ---------------------------------------------------------------------------
# NEDERLANDS
# ---------------------------------------------------------------------------
STRINGS["nl"] = {
    "quotes": [
        "Hallo! Ik ben de Kleine Prins.",
        "Heb je mijn roos gezien?",
        "De sterren zijn een miljoen kleine belletjes.",
        "Je ziet alleen goed met je hart. Het wezenlijke is onzichtbaar voor de ogen.",
        "Tem me alsjeblieft!",
        "Grote mensen begrijpen nooit iets vanzelf.",
        "Wat de woestijn mooi maakt, is dat ze ergens een put verbergt.",
        "Mijn roos… ik ben verantwoordelijk voor haar.",
        "Als je iemand temt, moet je erop rekenen een beetje te huilen.",
        "Het is de tijd die je voor je roos verloor die haar zo belangrijk maakt.",
    ],
    "fox": ["De vos: “Tem me!”", "De vos is er. Nu hebben we elkaar nodig."],
    "rose": ["Mijn roos is hier. Ik ben verantwoordelijk voor haar.", "Mijn roos… pas op haar doornen!"],
    "lamplighter": [
        "De lantaarnopsteker: “Goedendag, goedenavond!”",
        "Hij steekt elke minuut zijn lantaarn aan en uit.",
    ],
    "snake": ["De slang: “Je bent eenzaam onder de mensen.”", "De slang is er. Laten we niet bewegen."],
    "baobab": ["Een baobab! Trek hem uit voor hij de planeet splijt.", "Baobabzaden zijn gevaarlijk. Voorzichtig!"],
    "wake": ["Hm? Ik viel in slaap…", "Goedemorgen! Was ik sterren aan het tellen?", "O, jij bent het!"],
    "land": ["Au!", "Dat was te hoog…", "Oef!"],
    "menu": {
        "sit": "Gaan zitten",
        "stand": "Opstaan",
        "wake": "Wakker maken",
        "chat": "Praten (AI)…",
        "quote": "Een zin uit het boek zeggen",
        "walk": "Rondwandelen",
        "teleport": "Teleporteren",
        "settings": "Instellingen…",
        "respawn": "Naar het scherm halen",
        "quit": "Afsluiten",
    },
    "no_surface": "Er is hier geen ander oppervlak in de buurt…",
}

# ---------------------------------------------------------------------------
# POLSKI
# ---------------------------------------------------------------------------
STRINGS["pl"] = {
    "quotes": [
        "Cześć! Jestem Mały Książę.",
        "Widziałeś moją różę?",
        "Gwiazdy to milion małych dzwoneczków.",
        "Dobrze widzi się tylko sercem. Najważniejsze jest niewidoczne dla oczu.",
        "Oswoić mnie, proszę!",
        "Dorośli nigdy sami niczego nie rozumieją.",
        "Pustynię upiększa to, że gdzieś ukrywa studnię.",
        "Moja róża… jestem za nią odpowiedzialny.",
        "Kiedy kogoś oswoisz, musisz liczyć się z tym, że będziesz płakać.",
        "To czas, który poświęciłeś swojej róży, czyni ją tak ważną.",
    ],
    "fox": ["Lis: „Oswoić mnie!”", "Przyszedł lis. Teraz potrzebujemy siebie nawzajem."],
    "rose": ["Moja róża jest tutaj. Jestem za nią odpowiedzialny.", "Moja róża… uważaj na jej kolce!"],
    "lamplighter": [
        "Latarnik: „Dzień dobry, dobry wieczór!”",
        "Co minutę zapala i gasi swoją latarnię.",
    ],
    "snake": ["Wąż: „Jesteś samotny wśród ludzi.”", "Przyszedł wąż. Nie ruszajmy się."],
    "baobab": ["Baobab! Wyrwij go, zanim rozsadzi planetę.", "Nasiona baobabu są groźne. Uważaj!"],
    "wake": ["Hmm? Zasnąłem…", "Dzień dobry! Czy liczyłem gwiazdy?", "Ach, to ty!"],
    "land": ["Aua!", "To było za wysoko…", "Uff!"],
    "menu": {
        "sit": "Usiądź",
        "stand": "Wstań",
        "wake": "Obudź",
        "chat": "Rozmawiaj (AI)…",
        "quote": "Powiedz zdanie z książki",
        "walk": "Zacznij wędrować",
        "teleport": "Teleportuj się",
        "settings": "Ustawienia…",
        "respawn": "Przenieś na ekran",
        "quit": "Zakończ",
    },
    "no_surface": "Nie ma tu innej powierzchni…",
}

# ---------------------------------------------------------------------------
# RUSSKIY
# ---------------------------------------------------------------------------
STRINGS["ru"] = {
    "quotes": [
        "Привет! Я Маленький принц.",
        "Ты видел мою розу?",
        "Звёзды — это миллион маленьких колокольчиков.",
        "Зорко одно лишь сердце. Самого главного глазами не увидишь.",
        "Приручи меня, пожалуйста!",
        "Взрослые никогда ничего не понимают сами.",
        "Пустыню делает прекрасной то, что она где-то скрывает колодец.",
        "Моя роза… я за неё в ответе.",
        "Если ты кого-то приручил, придётся немного поплакать.",
        "Твоя роза так дорога тебе потому, что ты отдал ей время.",
    ],
    "fox": ["Лис: «Приручи меня!»", "Пришёл лис. Теперь мы нужны друг другу."],
    "rose": ["Моя роза здесь. Я за неё в ответе.", "Моя роза… берегись её шипов!"],
    "lamplighter": [
        "Фонарщик: «Добрый день, добрый вечер!»",
        "Он зажигает и гасит фонарь каждую минуту.",
    ],
    "snake": ["Змея: «Ты одинок среди людей.»", "Змея здесь. Не будем двигаться."],
    "baobab": ["Баобаб! Вырви его, пока он не расколол планету.", "Семена баобаба опасны. Осторожно!"],
    "wake": ["Мм? Я уснул…", "Доброе утро! Я считал звёзды?", "А, это ты!"],
    "land": ["Ай!", "Слишком высоко…", "Уф!"],
    "menu": {
        "sit": "Сесть",
        "stand": "Встать",
        "wake": "Разбудить",
        "chat": "Поговорить (ИИ)…",
        "quote": "Сказать фразу из книги",
        "walk": "Пойти гулять",
        "teleport": "Телепортироваться",
        "settings": "Настройки…",
        "respawn": "Вернуть на экран",
        "quit": "Выход",
    },
    "no_surface": "Рядом нет другой поверхности…",
}

# ---------------------------------------------------------------------------
# UKRAINSKA
# ---------------------------------------------------------------------------
STRINGS["uk"] = {
    "quotes": [
        "Привіт! Я Маленький принц.",
        "Ти бачив мою троянду?",
        "Зорі — це мільйон маленьких дзвіночків.",
        "Добре бачить лише серце. Найголовнішого очима не побачиш.",
        "Приручи мене, будь ласка!",
        "Дорослі ніколи нічого не розуміють самі.",
        "Пустелю робить прекрасною те, що вона десь ховає криницю.",
        "Моя троянда… я за неї відповідаю.",
        "Якщо ти когось приручив, доведеться трохи поплакати.",
        "Твоя троянда така дорога тобі, бо ти віддав їй свій час.",
    ],
    "fox": ["Лис: «Приручи мене!»", "Прийшов лис. Тепер ми потрібні одне одному."],
    "rose": ["Моя троянда тут. Я за неї відповідаю.", "Моя троянда… бережися її шипів!"],
    "lamplighter": [
        "Ліхтарник: «Добрий день, добрий вечір!»",
        "Він запалює й гасить ліхтар щохвилини.",
    ],
    "snake": ["Змія: «Ти самотній серед людей.»", "Змія тут. Не рухаймося."],
    "baobab": ["Баобаб! Вирви його, поки він не розколов планету.", "Насіння баобаба небезпечне. Обережно!"],
    "wake": ["Мм? Я заснув…", "Доброго ранку! Я рахував зорі?", "А, це ти!"],
    "land": ["Ай!", "Занадто високо…", "Уф!"],
    "menu": {
        "sit": "Сісти",
        "stand": "Встати",
        "wake": "Розбудити",
        "chat": "Поговорити (ШІ)…",
        "quote": "Сказати фразу з книжки",
        "walk": "Піти гуляти",
        "teleport": "Телепортуватися",
        "settings": "Налаштування…",
        "respawn": "Повернути на екран",
        "quit": "Вихід",
    },
    "no_surface": "Поруч немає іншої поверхні…",
}

# ---------------------------------------------------------------------------
# 中文 (简体)
# ---------------------------------------------------------------------------
STRINGS["zh"] = {
    "quotes": [
        "你好！我是小王子。",
        "你见过我的玫瑰吗？",
        "星星是一百万只小铃铛。",
        "只有用心才能看得清。重要的东西用眼睛是看不见的。",
        "请你……驯养我吧！",
        "大人们从来不会自己明白任何事。",
        "使沙漠显得美丽的，是它在某处藏着一口井。",
        "我的玫瑰……我要对她负责。",
        "一旦你驯养了谁，就难免要流一点眼泪。",
        "是你为你的玫瑰花费的时间，才使她如此重要。",
    ],
    "fox": ["狐狸：“请你驯养我吧！”", "狐狸来了。现在我们需要彼此。"],
    "rose": ["我的玫瑰在这里。我要对她负责。", "我的玫瑰……小心她的刺！"],
    "lamplighter": [
        "点灯人：“早上好，晚上好！”",
        "他每分钟都点灯又熄灯。",
    ],
    "snake": ["蛇：“在人群中你很孤独。”", "蛇来了。我们别动。"],
    "baobab": ["猴面包树！趁它还没撑裂星球，快拔掉。", "猴面包树的种子很危险。小心！"],
    "wake": ["嗯？我睡着了……", "早上好！我刚才在数星星吗？", "啊，是你！"],
    "land": ["哎哟！", "太高了……", "呼！"],
    "menu": {
        "sit": "坐下",
        "stand": "站起来",
        "wake": "叫醒",
        "chat": "聊天（AI）…",
        "quote": "说一句书里的台词",
        "walk": "开始散步",
        "teleport": "瞬移",
        "settings": "设置…",
        "respawn": "回到屏幕",
        "quit": "退出",
    },
    "no_surface": "附近没有别的平面……",
}

# ---------------------------------------------------------------------------
# 日本語
# ---------------------------------------------------------------------------
STRINGS["ja"] = {
    "quotes": [
        "こんにちは！ぼくは星の王子さま。",
        "ぼくのバラを見なかった？",
        "星は百万の小さな鈴なんだ。",
        "心で見なくちゃ、ものごとはよく見えない。かんじんなことは目に見えないんだ。",
        "ぼくを飼いならして！",
        "大人は自分だけでは何もわからないんだ。",
        "砂漠が美しいのは、どこかに井戸を隠しているからだよ。",
        "ぼくのバラ……ぼくが責任を持っているんだ。",
        "飼いならしたら、少しは泣くことになるよ。",
        "きみのバラが大切なのは、そのために時間を使ったからなんだ。",
    ],
    "fox": ["きつね：「ぼくを飼いならして！」", "きつねが来た。もうおたがいに必要なんだ。"],
    "rose": ["ぼくのバラが来た。責任を持っているんだ。", "ぼくのバラ……とげに気をつけて！"],
    "lamplighter": [
        "点灯夫：「おはよう、こんばんは！」",
        "毎分ランプを点けたり消したりしている。",
    ],
    "snake": ["へび：「人間の中ではきみはひとりぼっちだ。」", "へびが来た。動かないで。"],
    "baobab": ["バオバブだ！星を割る前に抜かなくちゃ。", "バオバブの種は危ない。気をつけて！"],
    "wake": ["うーん？寝ちゃってた……", "おはよう！星を数えてたのかな？", "あ、きみだ！"],
    "land": ["いたっ！", "高すぎたよ……", "うっ！"],
    "menu": {
        "sit": "すわる",
        "stand": "たつ",
        "wake": "起こす",
        "chat": "話す（AI）…",
        "quote": "本の一節を言う",
        "walk": "散歩する",
        "teleport": "テレポート",
        "settings": "設定…",
        "respawn": "画面に戻す",
        "quit": "終了",
    },
    "no_surface": "近くにほかの面がないよ……",
}

# ---------------------------------------------------------------------------
# 한국어
# ---------------------------------------------------------------------------
STRINGS["ko"] = {
    "quotes": [
        "안녕! 나는 어린 왕자야.",
        "내 장미를 봤어?",
        "별들은 백만 개의 작은 종소리야.",
        "마음으로 보아야 잘 볼 수 있어. 중요한 것은 눈에 보이지 않아.",
        "나를 길들여 줘!",
        "어른들은 혼자서는 아무것도 이해하지 못해.",
        "사막을 아름답게 만드는 건 어딘가에 우물을 숨기고 있다는 거야.",
        "내 장미… 나는 그 아이에게 책임이 있어.",
        "한 번 길들인 사람은 조금은 울게 되어 있어.",
        "네 장미가 소중한 건 그 아이에게 쓴 시간 때문이야.",
    ],
    "fox": ["여우: “나를 길들여 줘!”", "여우가 왔어. 이제 우리는 서로가 필요해."],
    "rose": ["내 장미가 왔어. 나는 책임이 있어.", "내 장미… 가시를 조심해!"],
    "lamplighter": [
        "점등인: “안녕하세요, 좋은 저녁입니다!”",
        "1분마다 등불을 켜고 꺼.",
    ],
    "snake": ["뱀: “사람들 사이에서 너는 외로워.”", "뱀이 왔어. 움직이지 말자."],
    "baobab": ["바오바브나무야! 별을 갈라놓기 전에 뽑아야 해.", "바오바브 씨앗은 위험해. 조심해!"],
    "wake": ["음? 잠들었나 봐…", "좋은 아침! 별을 세고 있었나?", "아, 너구나!"],
    "land": ["아야!", "너무 높았어…", "윽!"],
    "menu": {
        "sit": "앉기",
        "stand": "일어나기",
        "wake": "깨우기",
        "chat": "대화 (AI)…",
        "quote": "책 속 한 문장 말하기",
        "walk": "산책 시작",
        "teleport": "순간이동",
        "settings": "설정…",
        "respawn": "화면으로 가져오기",
        "quit": "종료",
    },
    "no_surface": "근처에 다른 표면이 없어…",
}

# ---------------------------------------------------------------------------
# हिन्दी
# ---------------------------------------------------------------------------
STRINGS["hi"] = {
    "quotes": [
        "नमस्ते! मैं छोटा राजकुमार हूँ।",
        "क्या तुमने मेरा गुलाब देखा?",
        "सितारे दस लाख छोटी घंटियाँ हैं।",
        "दिल से ही ठीक से देखा जा सकता है। ज़रूरी बात आँखों से नहीं दिखती।",
        "मुझे अपना बना लो!",
        "बड़े लोग कभी खुद कुछ नहीं समझते।",
        "रेगिस्तान को सुंदर बनाता है कि वह कहीं एक कुआँ छिपाए हुए है।",
        "मेरा गुलाब… उसकी ज़िम्मेदारी मेरी है।",
        "एक बार किसी को अपना बना लो, तो थोड़ा रोना पड़ता है।",
        "तुम्हारा गुलाब इसलिए कीमती है कि तुमने उस पर समय लगाया।",
    ],
    "fox": ["लोमड़ी: “मुझे अपना बना लो!”", "लोमड़ी आई। अब हम एक-दूसरे के हैं।"],
    "rose": ["मेरा गुलाब आया है। उसकी ज़िम्मेदारी मेरी है।", "मेरा गुलाब… उसके काँटों से बचो!"],
    "lamplighter": [
        "दीवट वाला: “नमस्कार, शुभ संध्या!”",
        "वह हर मिनट अपना दीया जलाता और बुझाता है।",
    ],
    "snake": ["साँप: “लोगों के बीच तुम अकेले हो।”", "साँप आया है। हिलना मत।"],
    "baobab": ["बाओबाब! ग्रह को चीरने से पहले इसे उखाड़ दो।", "बाओबाब के बीज खतरनाक हैं। सावधान!"],
    "wake": ["हम्म? मैं सो गया…", "सुप्रभात! क्या मैं तारे गिन रहा था?", "अरे, तुम हो!"],
    "land": ["आह!", "बहुत ऊँचा था…", "उफ़!"],
    "menu": {
        "sit": "बैठो",
        "stand": "खड़े हो",
        "wake": "जगाओ",
        "chat": "बात करो (AI)…",
        "quote": "किताब से एक पंक्ति कहो",
        "walk": "घूमने लगो",
        "teleport": "टेलीपोर्ट",
        "settings": "सेटिंग्स…",
        "respawn": "स्क्रीन पर लाओ",
        "quit": "बंद करो",
    },
    "no_surface": "यहाँ पास में कोई दूसरी सतह नहीं है…",
}

# ---------------------------------------------------------------------------
# বাংলা
# ---------------------------------------------------------------------------
STRINGS["bn"] = {
    "quotes": [
        "হ্যালো! আমি ছোট রাজপুত্র।",
        "আমার গোলাপটা দেখেছ?",
        "তারারা এক মিলিয়ন ছোট ঘণ্টা।",
        "হৃদয় দিয়েই ভালো করে দেখা যায়। আসল জিনিস চোখে দেখা যায় না।",
        "আমাকে পোষ মানাও!",
        "বড়রা কখনো নিজে থেকে কিছু বোঝে না।",
        "মরুভূমিকে সুন্দর করে তোলে এই যে সে কোথাও একটা কুয়ো লুকিয়ে রাখে।",
        "আমার গোলাপ… তার দায়িত্ব আমার।",
        "একবার কাউকে পোষ মানালে একটু কাঁদতে হয়।",
        "তোমার গোলাপ এত মূল্যবান কারণ তুমি তার পেছনে সময় দিয়েছ।",
    ],
    "fox": ["শিয়াল: “আমাকে পোষ মানাও!”", "শিয়াল এসেছে। এখন আমরা একে অন্যকে দরকার।"],
    "rose": ["আমার গোলাপ এসেছে। তার দায়িত্ব আমার।", "আমার গোলাপ… তার কাঁটায় সাবধান!"],
    "lamplighter": [
        "বাতি-জ্বালানো লোক: “শুভ দিন, শুভ সন্ধ্যা!”",
        "সে প্রতি মিনিটে বাতি জ্বালায় আর নেভায়।",
    ],
    "snake": ["সাপ: “মানুষের মাঝে তুমি একা।”", "সাপ এসেছে। নড়াচড়া করি না।"],
    "baobab": ["বাওবাব! গ্রহ ফাটানোর আগে একে উপড়ে ফেলো।", "বাওবাবের বীজ বিপজ্জনক। সাবধান!"],
    "wake": ["হুম? আমি ঘুমিয়ে পড়েছিলাম…", "শুভ সকাল! আমি তারা গুনছিলাম?", "ওহ, তুমি!"],
    "land": ["আহ!", "খুব উঁচু ছিল…", "উফ!"],
    "menu": {
        "sit": "বসো",
        "stand": "উঠো",
        "wake": "জাগাও",
        "chat": "কথা বলো (AI)…",
        "quote": "বই থেকে একটা লাইন বলো",
        "walk": "ঘুরতে শুরু করো",
        "teleport": "টেলিপোর্ট",
        "settings": "সেটিংস…",
        "respawn": "স্ক্রিনে আনো",
        "quit": "বন্ধ করো",
    },
    "no_surface": "এখানে কাছাকাছি অন্য কোনো পৃষ্ঠ নেই…",
}

# ---------------------------------------------------------------------------
# العربية
# ---------------------------------------------------------------------------
STRINGS["ar"] = {
    "quotes": [
        "مرحبًا! أنا الأمير الصغير.",
        "هل رأيت وردتي؟",
        "النجوم مليون جرس صغير.",
        "لا نرى بوضوح إلا بالقلب. الجوهر لا تراه العين.",
        "روّضني، أرجوك!",
        "الكبار لا يفهمون شيئًا بأنفسهم أبدًا.",
        "ما يجعل الصحراء جميلة أنها تخفي بئرًا في مكان ما.",
        "وردتي… أنا مسؤول عنها.",
        "حين تروّض أحدًا، لا بد أن تبكي قليلًا.",
        "الوقت الذي أهدرته من أجل وردتك هو ما يجعلها مهمة جدًا.",
    ],
    "fox": ["الثعلب: «روّضني!»", "جاء الثعلب. الآن نحن بحاجة إلى بعضنا."],
    "rose": ["وردتي هنا. أنا مسؤول عنها.", "وردتي… احذر أشواكها!"],
    "lamplighter": [
        "موقد المصابيح: «نهارك سعيد، مساؤك سعيد!»",
        "يشعل مصباحه ويطفئه كل دقيقة.",
    ],
    "snake": ["الأفعى: «أنت وحيد بين الناس.»", "جاءت الأفعى. لا نتحرك."],
    "baobab": ["شجرة الباوباب! اقتلعها قبل أن تشق الكوكب.", "بذور الباوباب خطيرة. انتبه!"],
    "wake": ["همم؟ لقد نمت…", "صباح الخير! هل كنت أعد النجوم؟", "آه، إنه أنت!"],
    "land": ["آخ!", "كان عاليًا جدًا…", "أوف!"],
    "menu": {
        "sit": "اجلس",
        "stand": "قف",
        "wake": "أيقظ",
        "chat": "تكلّم (ذكاء اصطناعي)…",
        "quote": "قل جملة من الكتاب",
        "walk": "ابدأ التجوّل",
        "teleport": "انتقال فوري",
        "settings": "الإعدادات…",
        "respawn": "أعِد إلى الشاشة",
        "quit": "خروج",
    },
    "no_surface": "لا يوجد سطح آخر قريب…",
}

# ---------------------------------------------------------------------------
# فارسی
# ---------------------------------------------------------------------------
STRINGS["fa"] = {
    "quotes": [
        "سلام! من شازده کوچولو هستم.",
        "گلم را دیدی؟",
        "ستاره‌ها یک میلیون زنگولهٔ کوچک‌اند.",
        "فقط با دل می‌توان خوب دید. چیزهای مهم با چشم دیده نمی‌شوند.",
        "مرا اهلی کن!",
        "بزرگ‌ترها هیچ‌وقت خودشان چیزی نمی‌فهمند.",
        "چیزی که کویر را زیبا می‌کند این است که جایی چاهی پنهان کرده.",
        "گلم… من مسئول او هستم.",
        "وقتی کسی را اهلی کردی، ناچار کمی گریه می‌کنی.",
        "زمانی که برای گلَت گذاشتی او را این‌قدر باارزش می‌کند.",
    ],
    "fox": ["روباه: «مرا اهلی کن!»", "روباه آمد. حالا به هم نیاز داریم."],
    "rose": ["گلم اینجاست. من مسئول او هستم.", "گلم… مراقب خارهایش باش!"],
    "lamplighter": [
        "فانوس‌بان: «روز بخیر، شب بخیر!»",
        "او هر دقیقه فانوسش را روشن و خاموش می‌کند.",
    ],
    "snake": ["مار: «تو میان آدم‌ها تنهایی.»", "مار آمد. تکان نخوریم."],
    "baobab": ["درخت بائوباب! قبل از اینکه سیاره را بشکافد، از جا بکنش.", "دانه‌های بائوباب خطرناک‌اند. مواظب باش!"],
    "wake": ["هوم؟ خوابم برد…", "صبح بخیر! داشتم ستاره می‌شمردم؟", "آه، خودتی!"],
    "land": ["آخ!", "خیلی بلند بود…", "اوف!"],
    "menu": {
        "sit": "بنشین",
        "stand": "بلند شو",
        "wake": "بیدار کن",
        "chat": "گفت‌وگو (هوش مصنوعی)…",
        "quote": "یک جمله از کتاب بگو",
        "walk": "شروع به گشتن کن",
        "teleport": "انتقال آنی",
        "settings": "تنظیمات…",
        "respawn": "به صفحه برگردان",
        "quit": "خروج",
    },
    "no_surface": "اینجا سطح دیگری نزدیک نیست…",
}

# ---------------------------------------------------------------------------
# BAHASA INDONESIA
# ---------------------------------------------------------------------------
STRINGS["id"] = {
    "quotes": [
        "Halo! Aku Pangeran Kecil.",
        "Pernahkah kau melihat mawarku?",
        "Bintang-bintang adalah sejuta lonceng kecil.",
        "Hanya dengan hati orang bisa melihat dengan benar. Yang penting tidak tampak oleh mata.",
        "Jinakkanlah aku!",
        "Orang dewasa tidak pernah mengerti apa pun sendirian.",
        "Yang membuat gurun indah adalah karena ia menyembunyikan sebuah sumur di suatu tempat.",
        "Mawarku… aku bertanggung jawab atasnya.",
        "Setelah menjinakkan seseorang, kau pasti akan menangis sedikit.",
        "Waktu yang kau habiskan untuk mawarmu itulah yang membuatnya begitu penting.",
    ],
    "fox": ["Rubah: “Jinakkanlah aku!”", "Rubah datang. Sekarang kami saling membutuhkan."],
    "rose": ["Mawarku ada di sini. Aku bertanggung jawab atasnya.", "Mawarku… hati-hati durinya!"],
    "lamplighter": [
        "Penyalakan lampu: “Selamat siang, selamat malam!”",
        "Dia menyalakan dan memadamkan lampunya setiap menit.",
    ],
    "snake": ["Ular: “Kau kesepian di antara manusia.”", "Ular datang. Jangan bergerak."],
    "baobab": ["Baobab! Cabut sebelum dia membelah planet.", "Biji baobab berbahaya. Hati-hati!"],
    "wake": ["Hmm? Aku tertidur…", "Selamat pagi! Apakah aku sedang menghitung bintang?", "Oh, kamu!"],
    "land": ["Aduh!", "Terlalu tinggi…", "Uf!"],
    "menu": {
        "sit": "Duduk",
        "stand": "Berdiri",
        "wake": "Bangunkan",
        "chat": "Bicara (AI)…",
        "quote": "Ucapkan kalimat dari buku",
        "walk": "Mulai berjalan-jalan",
        "teleport": "Teleportasi",
        "settings": "Pengaturan…",
        "respawn": "Bawa ke layar",
        "quit": "Keluar",
    },
    "no_surface": "Tidak ada permukaan lain di dekat sini…",
}

# ---------------------------------------------------------------------------
# TIẾNG VIỆT
# ---------------------------------------------------------------------------
STRINGS["vi"] = {
    "quotes": [
        "Xin chào! Tôi là Hoàng tử bé.",
        "Bạn có thấy bông hồng của tôi không?",
        "Các vì sao là một triệu chiếc chuông nhỏ.",
        "Người ta chỉ thấy rõ bằng trái tim. Điều cốt lõi thì mắt không thấy được.",
        "Hãy cảm hoá tôi!",
        "Người lớn chẳng bao giờ tự mình hiểu được điều gì.",
        "Điều làm sa mạc đẹp là nó giấu một cái giếng ở đâu đó.",
        "Bông hồng của tôi… tôi có trách nhiệm với cô ấy.",
        "Khi đã cảm hoá ai đó, ta đành phải khóc một chút.",
        "Chính thời gian bạn dành cho bông hồng khiến nó trở nên quan trọng.",
    ],
    "fox": ["Con cáo: “Hãy cảm hoá tôi!”", "Cáo đã đến. Giờ chúng ta cần nhau."],
    "rose": ["Hồng của tôi đây. Tôi có trách nhiệm với cô ấy.", "Hồng của tôi… coi chừng gai của cô ấy!"],
    "lamplighter": [
        "Người thắp đèn: “Chào ngày mới, chào buổi tối!”",
        "Anh ấy thắp và tắt đèn mỗi phút.",
    ],
    "snake": ["Con rắn: “Bạn cô đơn giữa loài người.”", "Rắn đến rồi. Đừng nhúc nhích."],
    "baobab": ["Cây bao báp! Nhổ nó trước khi nó chẻ đôi hành tinh.", "Hạt bao báp rất nguy hiểm. Cẩn thận!"],
    "wake": ["Hửm? Tôi ngủ mất rồi…", "Chào buổi sáng! Tôi đang đếm sao à?", "À, là bạn!"],
    "land": ["Ái!", "Cao quá…", "Ối!"],
    "menu": {
        "sit": "Ngồi xuống",
        "stand": "Đứng lên",
        "wake": "Đánh thức",
        "chat": "Trò chuyện (AI)…",
        "quote": "Nói một câu trong sách",
        "walk": "Bắt đầu đi dạo",
        "teleport": "Dịch chuyển",
        "settings": "Cài đặt…",
        "respawn": "Đưa về màn hình",
        "quit": "Thoát",
    },
    "no_surface": "Gần đây không có bề mặt nào khác…",
}


# ---------------------------------------------------------------------------
# Ek kitap alintilari (mevcut listelerin uzerine eklenir)
# ---------------------------------------------------------------------------
EXTRA_QUOTES = {}

EXTRA_QUOTES["en"] = [
    "You become responsible, forever, for what you have tamed.",
    "It is much harder to judge oneself than to judge others.",
    "I should have judged her by her deeds, not by her words.",
    "Only children know what they are looking for.",
    "Men have forgotten this truth. But you must not forget it.",
    "It is such a secret place, the land of tears.",
    "If you come at four in the afternoon, I shall begin to be happy at three.",
    "You will always be my friend. You will want to laugh with me.",
]

EXTRA_QUOTES["tr"] = [
    "Evcilleştirdiğin şeyden sonsuza kadar sorumlusun.",
    "İnsanın kendini yargılaması, başkasını yargılamasından çok daha zordur.",
    "Onu sözlerine göre değil, yaptıklarına göre yargılamalıydım.",
    "Ne aradıklarını bir tek çocuklar bilir.",
    "İnsanlar bu gerçeği unuttu. Ama sen unutmamalısın.",
    "Gözyaşlarının ülkesi ne kadar da gizemli bir yer.",
    "Dörtte geleceksen, saat üçte mutlu olmaya başlarım.",
    "Sonsuza kadar arkadaşım olacaksın. Benimle gülmek isteyeceksin.",
]

EXTRA_QUOTES["es"] = [
    "Uno se hace responsable para siempre de lo que ha domesticado.",
    "Es mucho más difícil juzgarse a sí mismo que juzgar a los demás.",
    "Debí juzgarla por sus actos, no por sus palabras.",
    "Solo los niños saben lo que buscan.",
    "Los hombres han olvidado esta verdad. Pero tú no debes olvidarla.",
    "Es un lugar tan secreto, la tierra de las lágrimas.",
    "Si vienes a las cuatro, empezaré a ser feliz a las tres.",
    "Siempre serás mi amigo. Querrás reír conmigo.",
]

EXTRA_QUOTES["fr"] = [
    "Tu deviens responsable pour toujours de ce que tu as apprivoisé.",
    "Il est bien plus difficile de se juger soi-même que de juger autrui.",
    "J'aurais dû la juger sur les actes et non sur les mots.",
    "Les enfants seuls savent ce qu'ils cherchent.",
    "Les hommes ont oublié cette vérité. Mais tu ne dois pas l'oublier.",
    "C'est un lieu si secret, le pays des larmes.",
    "Si tu viens à quatre heures, je commencerai d'être heureux à trois heures.",
    "Tu seras toujours mon ami. Tu auras envie de rire avec moi.",
]

EXTRA_QUOTES["de"] = [
    "Du bist für immer verantwortlich für das, was du dir gezähmt hast.",
    "Sich selbst zu richten ist viel schwerer, als andere zu richten.",
    "Ich hätte sie nach ihren Taten richten sollen, nicht nach ihren Worten.",
    "Nur die Kinder wissen, was sie suchen.",
    "Die Menschen haben diese Wahrheit vergessen. Aber du darfst sie nicht vergessen.",
    "Es ist ein so geheimer Ort, das Land der Tränen.",
    "Wenn du um vier kommst, werde ich um drei anfangen, glücklich zu sein.",
    "Du wirst immer mein Freund sein. Du wirst mit mir lachen wollen.",
]

EXTRA_QUOTES["it"] = [
    "Si diventa responsabili per sempre di ciò che si è addomesticato.",
    "È molto più difficile giudicare se stessi che giudicare gli altri.",
    "Avrei dovuto giudicarla dai fatti, non dalle parole.",
    "Solo i bambini sanno quello che cercano.",
    "Gli uomini hanno dimenticato questa verità. Ma tu non devi dimenticarla.",
    "È un luogo così segreto, il paese delle lacrime.",
    "Se vieni alle quattro, comincerò a essere felice alle tre.",
    "Sarai sempre mio amico. Avrai voglia di ridere con me.",
]

EXTRA_QUOTES["pt"] = [
    "A gente se torna responsável para sempre por aquilo que cativou.",
    "É muito mais difícil julgar a si mesmo do que julgar os outros.",
    "Eu deveria tê-la julgado pelos atos, não pelas palavras.",
    "Só as crianças sabem o que procuram.",
    "Os homens esqueceram essa verdade. Mas você não deve esquecê-la.",
    "É um lugar tão secreto, a terra das lágrimas.",
    "Se você vier às quatro, começarei a ser feliz às três.",
    "Você será sempre meu amigo. Vai querer rir comigo.",
]

EXTRA_QUOTES["nl"] = [
    "Je bent voor altijd verantwoordelijk voor wat je hebt getemd.",
    "Het is veel moeilijker om jezelf te beoordelen dan een ander.",
    "Ik had haar op haar daden moeten beoordelen, niet op haar woorden.",
    "Alleen kinderen weten wat ze zoeken.",
    "De mensen zijn deze waarheid vergeten. Maar jij mag haar niet vergeten.",
    "Het is zo'n geheime plek, het land van de tranen.",
    "Als je om vier uur komt, begin ik om drie uur al blij te zijn.",
    "Je zult altijd mijn vriend zijn. Je zult met me willen lachen.",
]

EXTRA_QUOTES["pl"] = [
    "Stajesz się na zawsze odpowiedzialny za to, co oswoiłeś.",
    "O wiele trudniej jest sądzić siebie niż innych.",
    "Powinienem był sądzić ją po czynach, a nie po słowach.",
    "Tylko dzieci wiedzą, czego szukają.",
    "Ludzie zapomnieli tej prawdy. Ale ty nie możesz jej zapomnieć.",
    "To takie sekretne miejsce, kraina łez.",
    "Jeśli przyjdziesz o czwartej, zacznę być szczęśliwy o trzeciej.",
    "Zawsze będziesz moim przyjacielem. Będziesz chciał się ze mną śmiać.",
]

EXTRA_QUOTES["ru"] = [
    "Ты навсегда в ответе за того, кого приручил.",
    "Судить себя гораздо труднее, чем судить других.",
    "Надо было судить её по делам, а не по словам.",
    "Одни только дети знают, чего ищут.",
    "Люди забыли эту истину. Но ты не должен её забывать.",
    "Это такое тайное место — страна слёз.",
    "Если ты придёшь в четыре, я начну счастливеть в три.",
    "Ты всегда будешь моим другом. Тебе захочется смеяться со мной.",
]

EXTRA_QUOTES["uk"] = [
    "Ти назавжди відповідаєш за того, кого приручив.",
    "Судити себе значно важче, ніж судити інших.",
    "Треба було судити її за вчинками, а не за словами.",
    "Лише діти знають, чого шукають.",
    "Люди забули цю істину. Але ти не повинен її забувати.",
    "Це таке таємне місце — країна сліз.",
    "Якщо ти прийдеш о четвертій, я почну радіти о третій.",
    "Ти завжди будеш моїм другом. Тобі захочеться сміятися зі мною.",
]
EXTRA_QUOTES["zh"] = [
    "你要永远对你驯养过的东西负责。",
    "审判自己比审判别人要难得多。",
    "我本该根据她的行为来判断，而不是她的话。",
    "只有孩子们知道自己在寻找什么。",
    "人们已经忘记了这个真理。但你不该忘记。",
    "眼泪的国度是多么神秘的地方。",
    "如果你下午四点来，我从三点就会开始感到幸福。",
    "你永远是我的朋友。你会想和我一起笑。",
]

EXTRA_QUOTES["ja"] = [
    "きみは、飼いならしたものに永遠に責任があるんだ。",
    "自分を裁くことは、他人を裁くよりずっと難しい。",
    "ことばじゃなく、行いで彼女を判断すべきだった。",
    "何を探しているのか知っているのは、子どもだけだ。",
    "大人はこの真実を忘れてしまった。でもきみは忘れてはいけない。",
    "涙の国は、とても秘密めいた場所なんだ。",
    "四時に来るなら、三時からぼくは幸せになるよ。",
    "きみはいつまでもぼくの友だちだ。ぼくと笑いたくなるよ。",
]

EXTRA_QUOTES["ko"] = [
    "너는 네가 길들인 것에 영원히 책임이 있어.",
    "자기를 판단하는 것은 남을 판단하는 것보다 훨씬 어려워.",
    "말이 아니라 행동으로 그 아이를 판단했어야 했어.",
    "무엇을 찾고 있는지 아는 건 아이들뿐이야.",
    "사람들은 이 진리를 잊었어. 하지만 너는 잊으면 안 돼.",
    "눈물의 나라는 참 비밀스러운 곳이야.",
    "네가 네 시에 온다면, 나는 세 시부터 행복해질 거야.",
    "너는 언제나 내 친구야. 나와 함께 웃고 싶어질 거야.",
]

EXTRA_QUOTES["hi"] = [
    "जिसे तुमने अपना बनाया, उसके लिए तुम हमेशा ज़िम्मेदार हो।",
    "दूसरों को आँकना आसान है, खुद को आँकना बहुत कठिन।",
    "मुझे उसके शब्दों से नहीं, उसके कामों से आँकना चाहिए था।",
    "क्या ढूँढ रहे हैं, यह सिर्फ़ बच्चे जानते हैं।",
    "लोग यह सच भूल गए हैं। पर तुम इसे मत भूलो।",
    "आँसुओं की भूमि कितनी गुप्त जगह है।",
    "अगर तुम चार बजे आओ, तो मैं तीन बजे से खुश होने लगूँगा।",
    "तुम हमेशा मेरे दोस्त रहोगे। तुम मेरे साथ हँसना चाहोगे।",
]

EXTRA_QUOTES["bn"] = [
    "যাকে পোষ মানিয়েছ, তার দায়িত্ব তোমার চিরকাল।",
    "নিজেকে বিচার করা অন্যদের বিচার করার চেয়ে অনেক কঠিন।",
    "তার কথা নয়, তার কাজ দেখে বিচার করা উচিত ছিল।",
    "শিশুরাই জানে তারা কী খুঁজছে।",
    "মানুষ এই সত্য ভুলে গেছে। কিন্তু তুমি ভুলো না।",
    "অশ্রুর দেশটা কত গোপন এক জায়গা।",
    "তুমি বিকেল চারটায় এলে, আমি তিনটেতেই খুশি হতে শুরু করব।",
    "তুমি চিরকাল আমার বন্ধু থাকবে। আমার সাথে হাসতে ইচ্ছে করবে।",
]

EXTRA_QUOTES["ar"] = [
    "أنت مسؤول إلى الأبد عمّا روّضته.",
    "محاسبة النفس أصعب بكثير من محاسبة الآخرين.",
    "كان عليّ أن أحكم عليها بأفعالها لا بكلماتها.",
    "الأطفال وحدهم يعرفون ما يبحثون عنه.",
    "نسي الناس هذه الحقيقة. لكن لا يجب أن تنساها.",
    "إنها لبقعة سرية، أرض الدموع.",
    "إن جئت في الرابعة، سأبدأ بالسعادة في الثالثة.",
    "ستبقى صديقي دائمًا. سترغب في الضحك معي.",
]

EXTRA_QUOTES["fa"] = [
    "تو تا همیشه مسئول چیزی هستی که اهلی کرده‌ای.",
    "قضاوت کردن دربارهٔ خودت بسیار سخت‌تر از قضاوت دربارهٔ دیگران است.",
    "باید او را از روی کردارش می‌سنجیدم، نه از روی حرف‌هایش.",
    "تنها بچه‌ها می‌دانند دنبال چه می‌گردند.",
    "مردم این حقیقت را فراموش کرده‌اند. ولی تو نباید فراموش کنی.",
    "سرزمین اشک‌ها جای بسیار پنهانی است.",
    "اگر ساعت چهار بیایی، از ساعت سه شاد شدن را آغاز می‌کنم.",
    "تو همیشه دوست من خواهی بود. دلت می‌خواهد با من بخندی.",
]

EXTRA_QUOTES["id"] = [
    "Kau bertanggung jawab selamanya atas apa yang telah kau jinakkan.",
    "Jauh lebih sulit menilai diri sendiri daripada menilai orang lain.",
    "Aku seharusnya menilainya dari perbuatannya, bukan dari kata-katanya.",
    "Hanya anak-anak yang tahu apa yang mereka cari.",
    "Orang-orang telah melupakan kebenaran ini. Tetapi kau tidak boleh melupakannya.",
    "Tempat yang begitu rahasia, negeri air mata.",
    "Jika kau datang pukul empat, aku akan mulai bahagia pukul tiga.",
    "Kau akan selalu menjadi temanku. Kau akan ingin tertawa bersamaku.",
]

EXTRA_QUOTES["vi"] = [
    "Bạn mãi mãi có trách nhiệm với những gì bạn đã cảm hoá.",
    "Đánh giá bản thân khó hơn nhiều so với đánh giá người khác.",
    "Lẽ ra tôi phải đánh giá cô ấy qua việc làm, chứ không phải lời nói.",
    "Chỉ trẻ con mới biết mình đang tìm kiếm điều gì.",
    "Người lớn đã quên mất sự thật này. Nhưng bạn đừng quên.",
    "Thật là một nơi bí mật, xứ sở của những giọt lệ.",
    "Nếu bạn đến lúc bốn giờ, tôi sẽ bắt đầu thấy hạnh phúc từ ba giờ.",
    "Bạn sẽ mãi là bạn của tôi. Bạn sẽ muốn cười cùng tôi.",
]


# ---------------------------------------------------------------------------
# Yardimcilar
# ---------------------------------------------------------------------------
def system_lang() -> str:
    """Isletim sisteminin dilini iki harfli kod olarak dondurur."""
    try:
        from PySide6.QtCore import QLocale

        name = QLocale.system().name()  # ornek: tr_TR
        code = (name or "en").split("_")[0].lower()
    except Exception:
        import locale

        code = (locale.getdefaultlocale()[0] or "en").split("_")[0].lower()
    return code if code in STRINGS else "en"


def resolve(pref: str) -> str:
    pref = (pref or "auto").lower()
    if pref == "auto":
        return system_lang()
    return pref if pref in STRINGS else "en"


def get(pref: str) -> dict:
    """Secilen dilin sozlugu (eksik anahtarlar Ingilizce'den tamamlanir)."""
    lang = resolve(pref)
    base = dict(STRINGS["en"])
    data = STRINGS.get(lang, {})
    base.update(data)
    # menu sozlugunu de birlestir
    menu = dict(STRINGS["en"]["menu"])
    menu.update(data.get("menu", {}))
    base["menu"] = menu
    # ana alintilar + ek alintilar
    quotes = list(data.get("quotes", STRINGS["en"]["quotes"]))
    quotes += list(EXTRA_QUOTES.get(lang, []))
    base["quotes"] = quotes

    # Yoldas repliklerini ikiye ayir:
    #   <tur>       -> Kucuk Prens'in yorumu (balon Prens'te)
    #   <tur>_said  -> yoldasin kendi sozu (balon yoldasta)
    for species, index in SAID_INDEX.items():
        lines = list(base.get(species, []))
        said = None
        if index is not None and 0 <= index < len(lines):
            said = _strip_quotes(lines.pop(index))
        base[species] = lines
        base[species + "_said"] = said

    return base

