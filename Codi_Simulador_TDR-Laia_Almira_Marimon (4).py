#TDR - Laia Almira Marimon
#Simulador de la Ruleta Europea amb estratègies d’aposta

#Llibreries necessàries
import tkinter as tk                                  #Llibreria principal per a la interfície gràfica
from tkinter import ttk, messagebox, filedialog
import random                                         #Per generar tirades aleatòries
import statistics                                     # Per calcular mitjanes
from datetime import datetime                         #Per afegir data i hora als informes
#Permet generar PDF amb taules i text
#El bloc try-except assegura que si la llibreria no està instal·lada, el programa segueixi funcionant
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

#Classe Ruleta

class Ruleta:

#Classe que representa la ruleta europea, té 37 números (0–36) i s’identifica si la bola cau a vermell o no
    def __init__(self):
        # Conjunt dels números de color vermell (segons la ruleta europea)
        self.vermell = {1, 3, 5, 7, 9, 12, 14, 16, 18,
                        19, 21, 23, 25, 27, 30, 32, 34, 36}

    def tirada(self):
#Simula una tirada a la ruleta. Retorna True si surt vermell (guanya l’aposta al vermell) o False si surt negre o el 0
        num = random.randint(0, 36)   # Genera un número aleatori entre 0 i 36
        return num in self.vermell    # Comprova si és un número vermell

#Estratègies
class Estrategia:
#Classe base per a totes les estratègies d’aposta
    def __init__(self, base=1):
        self.base = int(base)               # Aposta mínima inicial
        self.aposta_actual = int(base)      # Quantitat que s’aposta en cada tirada

    def reiniciar(self):
#Reinicia l’aposta a la quantitat base.
        self.aposta_actual = int(self.base)

    def aposta(self):
#Retorna l’import de l’aposta actual.
        return int(self.aposta_actual)

    def resultat(self, guanya):
#Actualitza el valor de l’aposta després de conèixer el resultat
        self.aposta_actual = int(self.base)

#Estratègies concretes

class Martingala(Estrategia):
#Estratègia Martingala: Si es perd, es dobla l’aposta, si es guanya, es torna a l’aposta base

    def resultat(self, guanya):
        if guanya:
            self.aposta_actual = self.base
        else:
            # Es limita l’aposta màxima a 10.000
            self.aposta_actual = min(self.aposta_actual * 2, 10000)


class Fibonacci(Estrategia):
#Estratègia Fibonacci: Es segueix la seqüència de Fibonacci per calcular la següent aposta
    def __init__(self, base=1):
        super().__init__(base)
        self.seq = [1, 1]
        self.index = 0

    def reiniciar(self):
#Reinicia la seqüència al començament
        self.seq = [1, 1]
        self.index = 0
        self.aposta_actual = self.base

    def aposta(self):
#Determina l’aposta actual segons la seqüència
        if self.index >= len(self.seq):
            self.seq.append(self.seq[-1] + self.seq[-2])
        return int(min(self.seq[self.index] * self.base, 10000))

    def resultat(self, guanya):
#Actualitza la posició dins la seqüència segons el resultat
        if guanya:
            self.index = max(0, self.index - 2)
        else:
            self.index += 1
            if self.index >= len(self.seq):
                self.seq.append(self.seq[-1] + self.seq[-2])
        self.aposta_actual = int(min(self.seq[self.index] * self.base, 10000))


class DAlembert(Estrategia):
#Estratègia d’Alembert: després d’una pèrdua, augmenta l’aposta en 1, després d’un guany, la redueix en 1 (fins al mínim base).

    def resultat(self, guanya):
        if guanya:
            self.aposta_actual = max(self.base, self.aposta_actual - 1)
        else:
            self.aposta_actual = min(self.aposta_actual + 1, 10000)


class ApostaFixa(Estrategia):
#Estratègia d’aposta constant: sempre aposta la mateixa quantitat, 1
    def resultat(self, guanya):
        self.aposta_actual = self.base


class ApostaAleatoria(Estrategia):
#Estratègia d’aposta aleatòria: aposta entre 1 i 10 de manera aleatòria
    def resultat(self, guanya):
        self.aposta_actual = random.randint(1, 10)

#Simulador de partides
class Simulador:
#Classe que gestiona la simulació completa d’una estratègia durant un nombre determinat de rondes.
    def __init__(self, estrategia_obj, rondes):
        self.estr = estrategia_obj       # Estratègia utilitzada
        self.rondes = int(rondes)        # Nombre de tirades a executar

    def jugar(self, retirar=True):
#Simula una partida amb l’estratègia donada.
        self.estr.reiniciar()
        saldo = 0
        ruleta = Ruleta()
        tirades_realitzades = 0
        total_apostat = 0

        # Bucle de tirades
        for i in range(1, self.rondes + 1):
            tirades_realitzades = i
            aposta = self.estr.aposta()
            total_apostat += aposta
            guanya = ruleta.tirada()

            # Actualització del balanç
            if guanya:
                saldo += aposta
            else:
                saldo -= aposta

            self.estr.resultat(guanya)

            # Si s’ha activat "retirar" i es guanya, s’acaba la simulació
            if guanya and retirar:
                break

        return tirades_realitzades, saldo, total_apostat

#Altres funcions

def crear_estrategia(nom):
#Crea una instància de l’estratègia seleccionada
    if nom == "Martingala": return Martingala()
    if nom == "Fibonacci": return Fibonacci()
    if nom == "Estratègia d'Alembert": return DAlembert()
    if nom == "Sempre el mateix valor": return ApostaFixa()
    return ApostaAleatoria()


def descripcio_estrategia(nom):
#Text descriptiu de cada estratègia per mostrar a la interfície
    textos = {
        "Martingala": "L’estratègia Martingala consisteix en doblar l'aposta en cas de pèrdua i tornar a apostar la mateixa unitat en cas de guany.",
        "Fibonacci": "L'estratègia Fibonacci segueix la seqüència matemàtica per ajustar l'aposta en funció dels resultats.",
        "Estratègia d'Alembert": "Augmenta una unitat després d'una pèrdua i redueix una després d'un guany.",
        "Sempre el mateix valor": "Aposta fixa: la mateixa quantitat a cada tirada.",
        "Valor aleatori": "Apostes en una quantitat aleatòria entre 1 i 10 que varien en cada tirada."
    }
    return textos.get(nom, "")

#Interfície gràfica (TKINTER)
class App:
    #Classe principal que defineix tota la interfície gràfica del simulador.
    def __init__(self, root):
        self.root = root
        root.title("Simulador Ruleta - TDR Laia Almira Marimon")
        root.geometry("1000x720")
        root.config(bg="#f0f0f0")

        #Capçalera principal de la finestra
        header = tk.Frame(root, bg="#f0f0f0")
        header.pack(fill="x", pady=12)
        tk.Label(header, text="Simulador de la Ruleta Europea", font=("Calibri", 20, "bold"),
                 bg="#f0f0f0").pack()

        #Text introductori amb explicació del programa
        sub = tk.Label(
            root,
            text=("Aquest programa simula el joc de la ruleta europea aplicant diverses estratègies d’aposta "
                  "com la Martingala, Fibonacci, d’Alembert, o bé apostes fixes o aleatòries, sempre apostant al vermell. "
                  "També permet analitzar l’esperança matemàtica i el balanç mitjà de cada estratègia, tant en el cas "
                  "de retirar-se després de la primera victòria com en continuar jugant totes les tirades."),
            bg="#f0f0f0", wraplength=900, justify="center"
        )
        sub.pack(pady=6)

        #Panell principal per a l'entrada de dades
        panel = tk.Frame(root, bg="#f0f0f0", padx=20, pady=10)
        panel.pack(pady=6, fill="x")

        #Selector desplegable per triar l’estratègia d’aposta
        tk.Label(panel, text="Estratègia:", bg="#f0f0f0").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.cmb = ttk.Combobox(
            panel,
            values=["Martingala", "Fibonacci", "Estratègia d'Alembert",
                    "Sempre el mateix valor", "Valor aleatori"],
            state="readonly", width=30
        )
        self.cmb.grid(row=0, column=1, sticky="w", padx=6, pady=6)
        self.cmb.set("")  # Inicialment buit

        #Entrada per definir el nombre de tirades per simulació (R)
        tk.Label(panel, text="Tirades per simulació (R):", bg="#f0f0f0").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.ent_r = tk.Entry(panel, width=12)
        self.ent_r.grid(row=1, column=1, sticky="w", padx=6, pady=6)

        #Entrada per definir el nombre total de simulacions (N)
        tk.Label(panel, text="Nombre de simulacions (N):", bg="#f0f0f0").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.ent_n = tk.Entry(panel, width=12)
        self.ent_n.grid(row=2, column=1, sticky="w", padx=6, pady=6)

        #Botó principal que inicia el càlcul i la simulació
        btn_frame = tk.Frame(root, bg="#f0f0f0")
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text="Calcular resultats", bg="#c8c8c8", font=("Calibri", 12, "bold"),
                  command=self.calcular).grid(row=0, column=0, padx=8)

        #Variables internes per guardar resultats i la finestra emergent de resultats
        self.ultims = None
        self.result_window = None

        #Ajust de la graella per millorar la disposició dels elements
        panel.columnconfigure(1, weight=1)

    #Funció principal que executa la simulació i calcula les dades finals
    def calcular(self):
        """
        Aquesta funció s’executa quan l’usuari prem el botó “Calcular resultats”.
        Recull les dades introduïdes, executa les simulacions per a les dues condicions:
          - Retirar-se després del primer guany.
          - No retirar-se (jugar totes les tirades).
        Calcula també l’esperança matemàtica experimental i la compara amb la teòrica.
        """
        #Comprovació que l’usuari hagi seleccionat una estratègia
        estr_nom = self.cmb.get().strip()
        if not estr_nom:
            messagebox.showerror("Error", "Seleccioneu una estratègia abans de calcular.")
            return

        #Validació de les dades d’entrada (R i N)
        try:
            R = int(self.ent_r.get())
            N = int(self.ent_n.get())
            if R <= 0 or N <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Introdueix valors positius vàlids per a R i N.")
            return

        #Inicialització del generador aleatori per garantir resultats diferents
        random.seed(datetime.now().timestamp())

        #Variables acumuladores per als resultats globals
        finals_ret = []   #Resultats amb retirada al primer guany
        finals_no = []    #Resultats sense retirada
        sum_bal_ret = sum_ap_ret = sum_bal_no = sum_ap_no = 0
        
        #Execució de totes les simulacions
        for sim_idx in range(1, N + 1):
            #Simulació amb retirada al primer guany
            e_ret = crear_estrategia(estr_nom)
            sim_ret = Simulador(e_ret, R)
            t_ret, bal_ret, ap_ret = sim_ret.jugar(retirar=True)
            finals_ret.append((sim_idx, t_ret, bal_ret, ap_ret))
            sum_bal_ret += bal_ret
            sum_ap_ret += ap_ret

            #Simulació sense retirada (es juga fins al final)
            e_no = crear_estrategia(estr_nom)
            sim_no = Simulador(e_no, R)
            t_no, bal_no, ap_no = sim_no.jugar(retirar=False)
            finals_no.append((sim_idx, t_no, bal_no, ap_no))
            sum_bal_no += bal_no
            sum_ap_no += ap_no

        #Càlcul de les esperances i balances mitjanes
        esperanca_ret = sum_bal_ret / sum_ap_ret if sum_ap_ret else 0
        esperanca_no = sum_bal_no / sum_ap_no if sum_ap_no else 0
        esperanca_teo = -1 / 37

        mitjana_ret = statistics.mean([b for (_, _, b, _) in finals_ret]) if finals_ret else 0
        mitjana_no = statistics.mean([b for (_, _, b, _) in finals_no]) if finals_no else 0

        #Guardem tots els resultats en un diccionari per a ús posterior
        self.ultims = {
            "estr": estr_nom, "R": R, "N": N,
            "finals_ret": finals_ret, "finals_no": finals_no,
            "mitjana_ret": mitjana_ret, "mitjana_no": mitjana_no,
            "esperanca_ret": esperanca_ret, "esperanca_no": esperanca_no,
            "esperanca_teo": esperanca_teo,
        }

        #Obre una nova finestra amb els resultats detallats
        self._mostrar_resultats_window(self.ultims)

    #Crea i mostra la finestra amb tots els resultats numèrics i taules
    def _mostrar_resultats_window(self, dades):
        """
        Mostra una nova finestra (Toplevel) amb tots els resultats numèrics.
        Inclou taules detallades per a cada simulació i permet generar un informe PDF.
        """
        #Si ja hi ha una finestra oberta, es tanca per evitar duplicats
        if self.result_window and tk.Toplevel.winfo_exists(self.result_window):
            self.result_window.destroy()

        #Creació de la finestra de resultats
        top = tk.Toplevel(self.root)
        top.title(f"Resultats: {dades['estr']}")
        top.geometry("1150x820")
        self.result_window = top

        #Implementació de desplaçament vertical (scroll)
        canvas = tk.Canvas(top, bg="#f7f7f7")
        scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg="#f7f7f7")
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        #Mostra el nom i descripció de l’estratègia seleccionada
        tk.Label(content, text=f"Estratègia: {dades['estr']}", font=("Calibri", 18, "bold"), bg="#f7f7f7").pack(pady=8)
        tk.Label(content, text=descripcio_estrategia(dades['estr']), bg="#f7f7f7",
                 wraplength=1000, justify="left").pack(pady=6)

        #Bloc amb la informació resumida (N, R, esperances, mitjanes)
        frame_vals = tk.Frame(content, bg="#ffffff", bd=1, relief="solid")
        frame_vals.pack(padx=40, pady=10, fill="x")

        info = [
            ("Simulacions (N)", dades["N"]),
            ("Tirades per simulació (R)", dades["R"]),
            ("Mitjana balanç (Retirar-se)", f"{dades['mitjana_ret']:.3f}"),
            ("Mitjana balanç (No retirar-se)", f"{dades['mitjana_no']:.3f}"),
            ("Esperança matemàtica (Retirar-se)", f"{dades['esperanca_ret']:.5f}"),
            ("Esperança matemàtica (No retirar-se)", f"{dades['esperanca_no']:.5f}"),
            ("Esperança matemàtica (teòrica)", f"{dades['esperanca_teo']:.5f}")
        ]
        #Mostra les dades generals en format etiquetes
        for t, v in info:
            r = tk.Frame(frame_vals, bg="#ffffff")
            r.pack(anchor="w", padx=8, pady=2)
            tk.Label(r, text=f"{t}: ", font=("Calibri", 11, "bold"), bg="#ffffff").pack(side="left")
            tk.Label(r, text=str(v), font=("Calibri", 11), bg="#ffffff").pack(side="left")

        #Creació de dues taules per comparar les simulacions amb i sense retirada
        tables_frame = tk.Frame(content, bg="#f7f7f7")
        tables_frame.pack(padx=10, pady=12, fill="both", expand=True)
        cols = ("Simulació", "Tirades", "Balanç final", "Total apostat")

        for idx, (title, dataset) in enumerate([
            ("RETIRAR-SE (primer guany)", dades["finals_ret"]),
            ("NO RETIRAR-SE (totes les tirades)", dades["finals_no"])
        ]):
            f = tk.Frame(tables_frame, bg="#f7f7f7")
            f.grid(row=0, column=idx, padx=10, sticky="nsew")
            tk.Label(f, text=title, font=("Calibri", 13, "bold"), bg="#f7f7f7").pack(pady=6)

            #Widget Treeview per mostrar les dades tabulades
            tree = ttk.Treeview(f, columns=cols, show="headings", height=20)
            for c in cols:
                tree.heading(c, text=c)
                tree.column(c, width=140, anchor="center")

            #Barra de desplaçament vertical per a cada taula
            vsb = ttk.Scrollbar(f, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")

            #Afegim les dades fila a fila a la taula
            for sim_idx, tirades, bal, total_ap in dataset:
                tree.insert("", "end", values=(sim_idx, tirades, bal, total_ap))

        #Botons inferiors per exportar dades o tancar la finestra
        btns = tk.Frame(content, bg="#f7f7f7")
        btns.pack(pady=16)
        tk.Button(btns, text="Descarregar PDF (dades)", bg="#d0d0d0", width=24,
                  command=self._desc_pdf_prompt).grid(row=0, column=0, padx=8)
        tk.Button(btns, text="Tancar", bg="#d0d0d0", width=12,
                  command=top.destroy).grid(row=0, column=1, padx=8)
            #Funció auxiliar per comprovar si és possible generar el PDF
    def _desc_pdf_prompt(self):
        """
        Comprova si hi ha resultats disponibles i si la llibreria 'reportlab' està instal·lada.
        En cas afirmatiu, inicia el procés per generar i desar l'informe en format PDF.
        """
        #Si encara no s’han generat resultats, mostra un missatge d’error
        if not self.ultims:
            messagebox.showerror("Error", "Cal generar resultats abans de desar el PDF.")
            return

        #Comprovació de la disponibilitat de la llibreria 'reportlab'
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror(
                "Error",
                "La llibreria 'reportlab' no està disponible.\nInstal·la-la amb:\n\npip install reportlab"
            )
            return

        #Si tot és correcte, es procedeix a la generació del PDF
        self.descarregar_pdf(self.ultims)

    #Funció que genera i desa l'informe complet de resultats en format PDF
    def descarregar_pdf(self, dades):
        """
        Genera un informe PDF amb totes les dades de la simulació realitzada.
        L'informe inclou:
         - Informació general de la configuració de la simulació.
         - Resultats globals (mitjanes i esperances).
         - Dades detallades de cada simulació en forma de taula.
        """
        #S’obre un quadre de diàleg per triar el nom i la ubicació del fitxer PDF
        fitxer = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Informe_{dades['estr']}.pdf"
        )
        #Si l’usuari cancel·la l’acció, la funció finalitza sense generar res
        if not fitxer:
            return

        #Creació del document PDF amb mida de pàgina A4
        doc = SimpleDocTemplate(fitxer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        #Capçalera del document amb títol i data d’execució
        elements.append(Paragraph(f"Informe de simulacions - Estratègia: {dades['estr']}", styles["Title"]))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        #Apartat: resultats generals de la simulació
        elements.append(Paragraph("Resultats generals:", styles["Heading2"]))
        data_general = [
            ["Estratègia", dades["estr"]],
            ["Tirades per simulació (R)", str(dades["R"])],
            ["Nombre de simulacions (N)", str(dades["N"])],
            ["Mitjana balanç (Retirar-se)", f"{dades['mitjana_ret']:.3f}"],
            ["Mitjana balanç (No retirar-se)", f"{dades['mitjana_no']:.3f}"],
            ["Esperança justa (Retirar-se)", f"{dades['esperanca_ret']:.5f}"],
            ["Esperança justa (No retirar-se)", f"{dades['esperanca_no']:.5f}"],
            ["Esperança teòrica (ruleta europea)", f"{dades['esperanca_teo']:.5f}"]
        ]

        #Creació de la taula amb els resultats generals
        tgen = Table(data_general, colWidths=[300, 220])
        tgen.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("ALIGN", (0, 0), (-1, -1), "LEFT")
        ]))
        elements.append(tgen)
        elements.append(Spacer(1, 12))

        #Apartat: taules amb els resultats detallats de totes les simulacions
        for title, data in [
            ("Retirar-se al primer guany", dades["finals_ret"]),
            ("No retirar-se (totes les tirades)", dades["finals_no"])
        ]:
            elements.append(Paragraph(f"Resultats per simulació - {title}", styles["Heading2"]))
            #Capçalera i contingut de cada taula
            data_t = [["Simulació", "Tirades jugades", "Balanç final", "Total apostat"]] + [
                [str(i), str(t), str(b), str(ap)] for (i, t, b, ap) in data
            ]
            table = Table(data_t, colWidths=[70, 100, 100, 100])
            table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("ALIGN", (1, 1), (-1, -1), "CENTER")
            ]))
            elements.append(table)
            elements.append(Spacer(1, 10))

        #Finalització i construcció del document PDF
        doc.build(elements)

        #Missatge confirmant la creació correcta del fitxer
        messagebox.showinfo("PDF creat", f"S'ha generat l'informe: {fitxer}")


#Inicialització de la finestra principal i execució del programa
root = tk.Tk()      #Creació de la finestra base de Tkinter
app = App(root)     #Instanciació de la classe principal del simulador
root.mainloop()     #Bucle principal de l’aplicació (manté la finestra activa)

