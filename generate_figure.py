import base64
import io

import numpy as np
from flask import render_template, Flask, request, redirect, url_for
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.integrate import odeint


def deriv(y, t, N, beta, gamma):
    S, I, R = y
    dSdt = -beta * S * I / N
    dIdt = beta * S * I / N - gamma * I
    dRdt = gamma * I
    return dSdt, dIdt, dRdt

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        popolazione = request.form["pop"]
        infetti = request.form["i"]
        r0_index = request.form["r0"]
        valori_di_input = popolazione + ',' + infetti + ',' + r0_index
        return redirect(url_for("plotView", values=valori_di_input))
    else:
        return render_template("form.html")

@app.route("/<values>", methods=["GET"])
def plotView(values):
    lista = values.split(",")
    N = int(lista[0])
    I0 = int(lista[1])
    r0_index = int(lista[2])
    R0 = 0
    S0 = N - I0 - R0
    gamma=0.25
    beta = r0_index*gamma
    t = np.linspace(0, 50, 50)
    y0 = S0, I0, R0
    ret = odeint(deriv, y0, t, args=(N, beta, gamma))
    S, I, R = ret.T
    # Generate plot
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    Titolo = "Modello SIR - R0 = " + str(r0_index)
    axis.set_title(Titolo)
    axis.set_xlabel("days from start")
    axis.set_ylabel("S, I, R")
    axis.grid()
    axis.plot(t, S, "b-", label='Suscettibili')
    axis.plot(t, I, "r-", label='Infetti')
    axis.plot(t, R, "g-", label='Guariti')
    axis.legend()

    # Convert plot to PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)

    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    return render_template("image.html", image=pngImageB64String)


if __name__ == '__main__':
    app.run(debug=True)
