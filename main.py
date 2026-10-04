import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
from datetime import datetime
import os
from PIL import Image

# استيراد مكتبات الـ PDF
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# محاولة استيراد مكتبات اللغة العربية 
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False

# إعدادات المظهر
ctk.set_appearance_mode("dark")

# تسجيل خط Arial ليدعم اللغة العربية في الـ PDF
try:
    pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:\\Windows\\Fonts\\arialbd.ttf'))
except:
    pass 

def ar_txt(text):
    if ARABIC_SUPPORT and any("\u0600" <= c <= "\u06FF" for c in str(text)): 
        reshaped_text = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped_text)
        return bidi_text
    return str(text)

class TrefalAppPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("UNITÉ TREFAL REGHAIA - نظام التسيير")
        self.geometry("1200x850")
        
        self.jobs = [
            "رئيس فرقة - Chef de Poste",
            "مُشغل آلة - Opérateur Machine",
            "مساعد مُشغل - Aide Opérateur",
            "سائق رافعة جسرية - Pontier"
        ]
        
        self.months = ["جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
        self.password = "1234"

        self.init_db()
        self.logo_path = "lOGO-trefal.png"
        self.show_login_screen()

    def init_db(self):
        self.conn = sqlite3.connect('trefal_v2.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS workers 
                            (id INTEGER PRIMARY KEY, name TEXT, job TEXT, balance INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS history 
                            (id INTEGER PRIMARY KEY, worker_id INTEGER, type TEXT, month TEXT, amount INTEGER, date TEXT)''')
        self.conn.commit()

    def show_login_screen(self):
        self.login_frame = ctk.CTkFrame(self, fg_color="#121212")
        self.login_frame.pack(expand=True, fill="both")
        box = ctk.CTkFrame(self.login_frame, width=400, height=500, corner_radius=20, border_width=2, border_color="#E67E22")
        box.place(relx=0.5, rely=0.5, anchor="center")
        try:
            img = Image.open(self.logo_path)
            logo = ctk.CTkImage(img, size=(120, 120))
            ctk.CTkLabel(box, image=logo, text="").pack(pady=30)
        except: pass
        ctk.CTkLabel(box, text="UNITÉ TREFAL", font=("Arial", 24, "bold"), text_color="#E67E22").pack()
        self.pass_entry = ctk.CTkEntry(box, show="*", width=250, placeholder_text="كلمة المرور", justify="center")
        self.pass_entry.pack(pady=20)
        ctk.CTkButton(box, text="دخول", fg_color="#E67E22", command=self.check_login).pack(pady=10)

    def check_login(self):
        if self.pass_entry.get() == self.password:
            self.login_frame.destroy()
            self.setup_main_interface()
        else:
            messagebox.showerror("خطأ", "كلمة المرور غير صحيحة!")

    def setup_main_interface(self):
        self.main_view = ctk.CTkFrame(self, fg_color="#1A1A1A")
        self.main_view.pack(expand=True, fill="both")
        self.show_dashboard()

    def show_dashboard(self):
        for widget in self.main_view.winfo_children(): widget.destroy()
        header = ctk.CTkFrame(self.main_view, fg_color="#E67E22", height=70, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="UNITÉ TREFAL REGHAIA - لوحة التحكم", font=("Arial", 22, "bold")).pack(pady=20)
        toolbar = ctk.CTkFrame(self.main_view, fg_color="transparent")
        toolbar.pack(pady=20, padx=20, fill="x")
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_worker_list())
        ctk.CTkEntry(toolbar, placeholder_text="🔍 بحث سريع...", width=350, textvariable=self.search_var).pack(side="left", padx=10)
        ctk.CTkButton(toolbar, text="+ إضافة عامل جديد", fg_color="#27ae60", command=self.add_worker_popup).pack(side="right")
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_view, fg_color="transparent")
        self.scroll_frame.pack(expand=True, fill="both", padx=30)
        ctk.CTkLabel(self.main_view, text="Brahim Lazaar — بـراهـيـم لـزعـر", font=("Garamond", 28, "bold"), text_color="#E67E22").place(relx=0.98, rely=0.98, anchor="se")
        self.refresh_worker_list()

    def refresh_worker_list(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        query = f"%{self.search_var.get()}%"
        self.cursor.execute("SELECT * FROM workers WHERE name LIKE ?", (query,))
        for w in self.cursor.fetchall():
            card = ctk.CTkFrame(self.scroll_frame, fg_color="#262626", height=80, corner_radius=15, border_width=1, border_color="#333")
            card.pack(fill="x", pady=5)
            name_btn = ctk.CTkButton(card, text=f"👤 {w[1]}", font=("Arial", 18, "bold"), fg_color="transparent", anchor="w", command=lambda x=w: self.open_worker_history(x))
            name_btn.pack(side="left", padx=20, fill="x", expand=True)
            ctk.CTkLabel(card, text=f"💼 {w[2]}", text_color="#AAA").pack(side="left", padx=20)
            ctk.CTkLabel(card, text=f"الرصيد: {w[3]} أيام", text_color="#E67E22", font=("Arial", 16, "bold")).pack(side="left", padx=30)
            ctk.CTkButton(card, text="🗑️", width=40, fg_color="#c0392b", command=lambda id=w[0]: self.delete_worker(id)).pack(side="right", padx=15)

    def open_worker_history(self, worker):
        for widget in self.main_view.winfo_children(): widget.destroy()
        
        # 1. الشريط العلوي
        header = ctk.CTkFrame(self.main_view, fg_color="#2c3e50", height=80)
        header.pack(fill="x")
        ctk.CTkButton(header, text="🔙 عودة", command=self.show_dashboard, fg_color="#7f8c8d", font=("Arial", 14, "bold")).pack(side="right", padx=20, pady=20)
        ctk.CTkLabel(header, text=f"سجل: {worker[1]} | {worker[2]}", font=("Arial", 20, "bold")).pack(side="right", padx=30)
        ctk.CTkButton(header, text="🖨️ طباعة الورقة الرسمية", fg_color="#2980b9", font=("Arial", 14, "bold"), command=lambda: self.export_table_pdf(worker)).pack(side="left", padx=20)
        
        # 2. شريط الأدوات
        action_bar = ctk.CTkFrame(self.main_view, fg_color="#1e1e1e", corner_radius=10)
        action_bar.pack(pady=10, padx=20, fill="x", ipadx=10, ipady=10)
        
        now = datetime.now()
        self.sel_year = ctk.StringVar(value=str(now.year))
        self.sel_month = ctk.StringVar(value=self.months[now.month-1])
        self.sel_day = ctk.StringVar(value=str(now.day))
        
        date_frame = ctk.CTkFrame(action_bar, fg_color="transparent")
        date_frame.pack(side="right", padx=10)
        
        ctk.CTkLabel(date_frame, text=":تاريخ العملية", font=("Arial", 16, "bold"), text_color="#E67E22").pack(side="right", padx=15)
        ctk.CTkOptionMenu(date_frame, values=[str(y) for y in range(2020, 2035)], variable=self.sel_year, width=90).pack(side="right", padx=5)
        ctk.CTkOptionMenu(date_frame, values=self.months, variable=self.sel_month, width=110).pack(side="right", padx=5)
        ctk.CTkOptionMenu(date_frame, values=[str(d) for d in range(1, 32)], variable=self.sel_day, width=70).pack(side="right", padx=5)
        
        btn_frame = ctk.CTkFrame(action_bar, fg_color="transparent")
        btn_frame.pack(side="left", padx=10)
        
        ctk.CTkButton(btn_frame, text="+ إضافة يوم", fg_color="#f1c40f", text_color="black", font=("Arial", 14, "bold"), command=lambda: self.update_balance(worker, 1)).pack(side="right", padx=10)
        ctk.CTkButton(btn_frame, text="- استرجاع يوم", fg_color="#e74c3c", font=("Arial", 14, "bold"), command=lambda: self.update_balance(worker, -1)).pack(side="right", padx=10)

        # 3. الجدول السنوي
        table_container = ctk.CTkFrame(self.main_view, fg_color="#121212")
        table_container.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(table_container, text="الجدول السنوي للتوثيق (مطابق للورقة)", font=("Arial", 16, "bold"), text_color="#E67E22").pack(pady=5)
        
        table_frame = ctk.CTkFrame(table_container, fg_color="#555", corner_radius=0) 
        table_frame.pack(fill="x", padx=5, pady=5)
        
        for i in range(13):
            table_frame.grid_columnconfigure(i, weight=1, uniform="col")
            
        cols = ["البيان"] + self.months
        
        for idx, text in enumerate(cols):
            grid_col = 12 - idx
            lbl = ctk.CTkLabel(table_frame, text=text, font=("Arial", 14, "bold"), fg_color="#34495e", text_color="white", corner_radius=0, height=40)
            lbl.grid(row=0, column=grid_col, padx=1, pady=1, sticky="nsew")
            
        add_row = ["أيام إضافية (+)"]
        rec_row = ["أيام الاسترجاع (-)"]
        net_row = ["الرصيد الصافي (=)"]
        
        for m in self.months:
            self.cursor.execute("SELECT SUM(amount) FROM history WHERE worker_id=? AND month=? AND amount > 0", (worker[0], m))
            a = self.cursor.fetchone()[0] or 0
            add_row.append(str(a) if a > 0 else "-")
            
            self.cursor.execute("SELECT SUM(amount) FROM history WHERE worker_id=? AND month=? AND amount < 0", (worker[0], m))
            r = self.cursor.fetchone()[0] or 0
            rec_row.append(str(abs(r)) if r < 0 else "-")
            
            net = a - abs(r)
            net_row.append(str(net) if net != 0 else "-")
            
        for r_idx, row_data in enumerate([add_row, rec_row, net_row], start=1):
            for c_idx, text in enumerate(row_data):
                grid_col = 12 - c_idx 
                bg_color = "#2c3e50" if c_idx == 0 else "#262626"
                txt_color = "white"
                if r_idx == 1 and c_idx > 0 and text != "-": txt_color = "#2ecc71"
                if r_idx == 2 and c_idx > 0 and text != "-": txt_color = "#e74c3c"
                if r_idx == 3 and c_idx > 0 and text != "-": 
                    txt_color = "#f1c40f" if int(text) > 0 else "white"
                font = ("Arial", 14, "bold") if c_idx == 0 else ("Arial", 16, "bold")
                lbl = ctk.CTkLabel(table_frame, text=text, font=font, fg_color=bg_color, text_color=txt_color, corner_radius=0, height=35)
                lbl.grid(row=r_idx, column=grid_col, padx=1, pady=1, sticky="nsew")

        # 4. سجل العمليات التفصيلي مع أزرار الحذف
        hist_header_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        hist_header_frame.pack(fill="x", padx=30, pady=(15, 0))
        
        # زر حذف كل السجل دفعة واحدة
        ctk.CTkButton(hist_header_frame, text="🗑️ مسح كل السجل", fg_color="#c0392b", hover_color="#922b21", font=("Arial", 14, "bold"),
                      command=lambda w=worker: self.delete_all_history(w)).pack(side="left")
                      
        list_lbl = ctk.CTkLabel(hist_header_frame, text="سجل التواريخ والعمليات التفصيلي", font=("Arial", 16, "bold"), text_color="#AAA")
        list_lbl.pack(side="right")
        
        hist_frame = ctk.CTkScrollableFrame(self.main_view, fg_color="#121212")
        hist_frame.pack(expand=True, fill="both", padx=20, pady=5)
        
        self.cursor.execute("SELECT * FROM history WHERE worker_id=? ORDER BY date DESC, id DESC", (worker[0],))
        records = self.cursor.fetchall()
        
        if not records:
            ctk.CTkLabel(hist_frame, text="لا توجد عمليات مسجلة حالياً.", text_color="#777", font=("Arial", 14)).pack(pady=20)
            
        for h in records:
            color = "#f1c40f" if h[4] > 0 else "#e74c3c"
            bg_color = "#2a2a2a" if h[4] > 0 else "#332222"
            line = ctk.CTkFrame(hist_frame, fg_color=bg_color, corner_radius=8, height=45)
            line.pack(fill="x", pady=3)
            
            op_text = f"العملية: {h[2]} ({abs(h[4])} يوم)   |   الشهر المعني: {h[3]}   |   سُجلت بتاريخ: {h[5]}"
            ctk.CTkLabel(line, text=op_text, text_color=color, font=("Arial", 15, "bold")).pack(side="right", padx=20, pady=8)
            
            # زر حذف العملية في حال تم إدخالها بالخطأ (يحذفها ويسترجع الرصيد)
            ctk.CTkButton(line, text="🗑️ حذف العملية", width=80, fg_color="#c0392b", hover_color="#922b21", font=("Arial", 12, "bold"), 
                          command=lambda hid=h[0], w=worker, amt=h[4]: self.delete_history_record(hid, w, amt)).pack(side="left", padx=15)

    def update_balance(self, worker, amt):
        m = self.sel_month.get()
        y = self.sel_year.get()
        day = self.sel_day.get()
        current_time = datetime.now().strftime("%H:%M")
        month_idx = self.months.index(m) + 1
        d = f"{y}-{month_idx:02d}-{int(day):02d} {current_time}"
        type_str = "إضافة" if amt > 0 else "استرجاع"
        
        self.cursor.execute("UPDATE workers SET balance = balance + ? WHERE id = ?", (amt, worker[0]))
        self.cursor.execute("INSERT INTO history (worker_id, type, month, amount, date) VALUES (?, ?, ?, ?, ?)", (worker[0], type_str, m, amt, d))
        self.conn.commit()
        
        self.cursor.execute("SELECT * FROM workers WHERE id=?", (worker[0],))
        updated_worker = self.cursor.fetchone()
        self.open_worker_history(updated_worker)

    def delete_history_record(self, hist_id, worker, amt):
        # حذف سجل معين وإلغاء تأثيره على الرصيد بالكامل دون تخريب التواريخ الأخرى
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذه العملية نهائياً؟ سيتم تعديل الرصيد تلقائياً ليعود كما كان."):
            self.cursor.execute("UPDATE workers SET balance = balance - ? WHERE id = ?", (amt, worker[0]))
            self.cursor.execute("DELETE FROM history WHERE id = ?", (hist_id,))
            self.conn.commit()
            
            self.cursor.execute("SELECT * FROM workers WHERE id=?", (worker[0],))
            updated_worker = self.cursor.fetchone()
            self.open_worker_history(updated_worker)

    def delete_all_history(self, worker):
        # مسح كل السجل وتصفير رصيد العامل
        if messagebox.askyesno("تأكيد خطير", "هل أنت متأكد من حذف **كل** السجل التاريخي لهذا العامل؟\nسيتم تصفير الرصيد ومسح كل العمليات نهائياً!"):
            self.cursor.execute("DELETE FROM history WHERE worker_id = ?", (worker[0],))
            self.cursor.execute("UPDATE workers SET balance = 0 WHERE id = ?", (worker[0],))
            self.conn.commit()
            
            self.cursor.execute("SELECT * FROM workers WHERE id=?", (worker[0],))
            updated_worker = self.cursor.fetchone()
            self.open_worker_history(updated_worker)

    def add_worker_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("عامل جديد")
        popup.geometry("400x400")
        popup.attributes("-topmost", True)
        ctk.CTkLabel(popup, text="الاسم الكامل:").pack(pady=10)
        name_ent = ctk.CTkEntry(popup, width=300)
        name_ent.pack()
        ctk.CTkLabel(popup, text="المنصب:").pack(pady=10)
        job_menu = ctk.CTkOptionMenu(popup, values=self.jobs, width=300)
        job_menu.pack()
        def save():
            if name_ent.get():
                self.cursor.execute("INSERT INTO workers (name, job, balance) VALUES (?, ?, 0)", (name_ent.get(), job_menu.get()))
                self.conn.commit()
                popup.destroy()
                self.refresh_worker_list()
        ctk.CTkButton(popup, text="حفظ", fg_color="#27ae60", command=save).pack(pady=30)

    def delete_worker(self, wid):
        if messagebox.askyesno("تأكيد", "حذف العامل وسجله؟"):
            self.cursor.execute("DELETE FROM workers WHERE id=?", (wid,))
            self.cursor.execute("DELETE FROM history WHERE worker_id=?", (wid,))
            self.conn.commit()
            self.refresh_worker_list()

    def export_table_pdf(self, worker):
        if not ARABIC_SUPPORT:
            messagebox.showwarning("تحذير", "لم يتم تثبيت مكتبات اللغة العربية.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"Fiche_{worker[1]}.pdf")
        if not path: return

        try:
            doc = SimpleDocTemplate(path, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            elements = []
            
            arabic_title_style = ParagraphStyle(name='ArabicTitle', fontName='Arial-Bold', fontSize=18, alignment=1, spaceAfter=10, textColor=colors.HexColor("#2c3e50"))
            arabic_normal_style = ParagraphStyle(name='ArabicNormal', fontName='Arial', fontSize=12, alignment=0, spaceAfter=8)
            section_title_style = ParagraphStyle(name='SecTitle', fontName='Arial-Bold', fontSize=14, alignment=2, spaceBefore=20, spaceAfter=10, textColor=colors.HexColor("#E67E22"))

            elements.append(Paragraph(f"<font size=20 color='#E67E22'><b>UNITÉ TREFAL REGHAIA</b></font>", arabic_title_style))
            elements.append(Paragraph(ar_txt("FICHE DE POINTAGE ET RÉCUPÉRATION / بطاقة التنقيط والاسترجاع"), arabic_title_style))
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Nom et Prénom / {ar_txt('الاسم واللقب')} :</b> {ar_txt(worker[1])}", arabic_normal_style))
            elements.append(Paragraph(f"<b>Poste / {ar_txt('المنصب')} :</b> {ar_txt(worker[2])}", arabic_normal_style))
            elements.append(Spacer(1, 15))

            header = [ar_txt('التفاصيل / Détails')] + [ar_txt(m) for m in self.months]
            add_row = [ar_txt('أيام إضافية (+)')]
            rec_row = [ar_txt('أيام مسترجعة (-)')]
            net_row = [ar_txt('الرصيد الشهري (=)')]

            for m in self.months:
                self.cursor.execute("SELECT SUM(amount) FROM history WHERE worker_id=? AND month=? AND amount > 0", (worker[0], m))
                a = self.cursor.fetchone()[0] or 0
                add_row.append(str(a))
                self.cursor.execute("SELECT SUM(amount) FROM history WHERE worker_id=? AND month=? AND amount < 0", (worker[0], m))
                r = self.cursor.fetchone()[0] or 0
                rec_row.append(str(abs(r)))
                net_row.append(str(a - abs(r)))

            t = Table([header, add_row, rec_row, net_row], colWidths=[120] + [55]*12)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            elements.append(t)

            elements.append(Paragraph(ar_txt("Détails des Mouvements / سجل الحركات التفصيلي (تاريخ الإضافة/الاسترجاع)"), section_title_style))
            
            self.cursor.execute("SELECT type, month, amount, date FROM history WHERE worker_id=? ORDER BY id DESC", (worker[0],))
            history_data = self.cursor.fetchall()
            
            if history_data:
                hist_table_data = [[ar_txt('تاريخ وساعة العملية'), ar_txt('القيمة'), ar_txt('الشهر المعني'), ar_txt('نوع العملية')]]
                for h in history_data:
                    op_type = "➕ " + ar_txt("إضافة") if h[2] > 0 else "➖ " + ar_txt("استرجاع")
                    row = [h[3], f"{h[2]} " + ar_txt("أيام"), ar_txt(h[1]), op_type]
                    hist_table_data.append(row)
                
                ht = Table(hist_table_data, colWidths=[180, 100, 100, 150])
                h_style = [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#34495e")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                ]
                
                for i, row in enumerate(history_data):
                    color = colors.HexColor("#ebfef2") if row[2] > 0 else colors.HexColor("#fef2f2")
                    text_color = colors.darkgreen if row[2] > 0 else colors.red
                    h_style.append(('BACKGROUND', (0, i+1), (-1, i+1), color))
                    h_style.append(('TEXTCOLOR', (3, i+1), (3, i+1), text_color))

                ht.setStyle(TableStyle(h_style))
                elements.append(ht)
            else:
                elements.append(Paragraph(ar_txt("لا توجد حركات مسجلة حالياً."), arabic_normal_style))

            # وضع الرصيد الإجمالي في الأخير كما طلبت
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(f"<b>Solde Global / {ar_txt('الرصيد الإجمالي النهائي')} :</b> <font color='red'><b>{worker[3]} {ar_txt('أيام')}</b></font>", arabic_title_style))
            elements.append(Spacer(1, 30))
            
            sig_data = [[ar_txt('رئيس القسم / Chef de Section'), ar_txt('رئيس الفرقة / Chef de Poste'), ar_txt('توقيع العامل / L\'employé')]]
            sig_table = Table(sig_data, colWidths=[250, 250, 250])
            sig_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, -1), 'Arial-Bold')]))
            elements.append(sig_table)

            doc.build(elements)
            messagebox.showinfo("نجاح", "تم استخراج الورقة الرسمية بنجاح!")
            os.startfile(path)
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الطباعة: {e}")

if __name__ == "__main__":
    app = TrefalAppPro()
    app.mainloop()