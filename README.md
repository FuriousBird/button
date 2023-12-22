# button
<p>Converting a toy button into a macro keyboard.</p>
<img src="20231126_200017.jpg" alt="button pic" style="width:50%; max-width:150px !important;">

<p>Working over serial, a python app receives clicks and executes actions.</p>
<img src="https://github.com/FuriousBird/button/assets/44238459/b38f9e6a-18c5-455d-80ad-fb10edaaa052)" style="width:50%; max-width:150px !important;">

```
Attention a bien modifier la librairie pynput en fonction de la plateforme de destination.
fichier : pynput/keyboard/__init__.py
modification (linux) (pour windows _win32 au lieu de xorg) :

import pynput.keyboard._xorg as _xorg

#backend = backend(__name__)
backend = _xorg
```