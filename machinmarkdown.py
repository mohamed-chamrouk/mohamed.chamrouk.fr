import markdown
text = "<p>Bienvenue sur mon tout nouveau site web !</p>
        <p>Vous trouverez ici tout ce qui me concerne, comme notamment mon CV ou encore mon portfolio (d'autres sections s'ajouteront avec le temps..).<br>
        Le site est encore en cours de construction donc les changements ne serront pas rares.</p>

        <p>Bonne navigation !

      </p>"

output = markdown.markdown(text)
print(output)
