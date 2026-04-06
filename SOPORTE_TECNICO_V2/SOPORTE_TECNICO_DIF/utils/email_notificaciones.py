"""
Módulo de notificaciones por correo electrónico - Sistema DIF
Todas las notificaciones llegan a: informatica@difelamarques.gob.mx
"""
from datetime import datetime
from flask_mail import Message


class EmailNotificaciones:

    def __init__(self, mail, admin_email='informatica@difelmarques.gob.mx'):
        self.mail = mail
        self.admin_email = admin_email  # siempre recibe copia

    def _destinatarios(self, email_usuario=None):
        """El admin SIEMPRE recibe. El usuario también si tiene email."""
        destinatarios = [self.admin_email]
        if email_usuario and email_usuario != self.admin_email:
            destinatarios.append(email_usuario)
        return destinatarios

    def enviar_ticket_creado(self, ticket, email_usuario=None):
        msg = Message(
            subject=f'🎫 [DIF Soporte] Nuevo Ticket #{ticket["folio"]}',
            recipients=self._destinatarios(email_usuario)
        )
        msg.body = f"""
SISTEMA DE SOPORTE TÉCNICO - DIF EL MARQUES
============================================
NUEVO TICKET REGISTRADO

📋 Folio:     #{ticket["folio"]}
📌 Título:    {ticket["titulo"]}
👤 Usuario:   {ticket.get("nombre_usuario", "N/A")}
🏢 Área:      {ticket.get("area_usuario", "N/A")}
⚡ Prioridad: {ticket.get("prioridad", "N/A")}
🕐 Fecha:     {datetime.now().strftime('%d/%m/%Y %H:%M')}

El departamento de Informática atenderá su solicitud a la brevedad.

--------------------------------------------
Sistema de Soporte Técnico DIF El Marques
informatica@difelmarques.gob.mx
        """
        self.mail.send(msg)

    def enviar_ticket_actualizado(self, ticket, email_usuario=None):
        msg = Message(
            subject=f'🔄 [DIF Soporte] Ticket Actualizado #{ticket["folio"]}',
            recipients=self._destinatarios(email_usuario)
        )
        msg.body = f"""
SISTEMA DE SOPORTE TÉCNICO - DIF EL MARQUES
============================================
TICKET ACTUALIZADO

📋 Folio:    #{ticket["folio"]}
📌 Título:   {ticket["titulo"]}
📊 Estado:   {ticket["estado"]}
🕐 Fecha:    {datetime.now().strftime('%d/%m/%Y %H:%M')}

--------------------------------------------
Sistema de Soporte Técnico DIF El Marques
informatica@difelmarques.gob.mx
        """
        self.mail.send(msg)

    def enviar_ticket_resuelto(self, ticket, email_usuario=None):
        msg = Message(
            subject=f'✅ [DIF Soporte] Ticket Resuelto #{ticket["folio"]}',
            recipients=self._destinatarios(email_usuario)
        )
        msg.body = f"""
SISTEMA DE SOPORTE TÉCNICO - DIF EL MARQUES
============================================
TICKET RESUELTO

📋 Folio:          #{ticket["folio"]}
📌 Título:         {ticket["titulo"]}
👨‍💻 Atendido por:  {ticket.get("nombre_tecnico", "Equipo de Informática")}
🕐 Fecha:          {datetime.now().strftime('%d/%m/%Y %H:%M')}

Si el problema persiste, puede abrir un nuevo ticket.

--------------------------------------------
Sistema de Soporte Técnico DIF El Marques
informatica@difelamarques.gob.mx
        """
        self.mail.send(msg)

    def enviar_ticket_cerrado(self, ticket, email_usuario=None):
        msg = Message(
            subject=f'🔒 [DIF Soporte] Ticket Cerrado #{ticket["folio"]}',
            recipients=self._destinatarios(email_usuario)
        )
        msg.body = f"""
SISTEMA DE SOPORTE TÉCNICO - DIF EL MARQUES
============================================
TICKET CERRADO

📋 Folio:        #{ticket["folio"]}
📌 Título:       {ticket["titulo"]}
📅 Fecha cierre: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Gracias por usar el Sistema de Soporte Técnico DIF.

--------------------------------------------
Departamento de Informática - DIF El Marques
informatica@difelmarques.gob.mx
        """
        self.mail.send(msg)