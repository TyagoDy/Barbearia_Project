import { useState, useEffect } from "react"

function App() {
  // Dados principais
  const [barbers, setBarbers] = useState([])
  const [clients, setClients] = useState([])
  const [appointments, setAppointments] = useState([])

  // Formulário - Novo Barbeiro
  const [newBarberName, setNewBarberName] = useState("")
  const [newBarberSpecialty, setNewBarberSpecialty] = useState("")

  // Formulário - Novo Cliente
  const [newClientName, setNewClientName] = useState("")
  const [newClientPhone, setNewClientPhone] = useState("")

  // Formulário - Novo Agendamento
  const [selectedBarberId, setSelectedBarberId] = useState("")
  const [selectedClientId, setSelectedClientId] = useState("")
  const [bookingDate, setBookingDate] = useState("")
  const [paymentMethod, setPaymentMethod] = useState("Cartão de Crédito")

  // Estado de Alerta/Feedback
  const [alert, setAlert] = useState(null)

  // API Base URL (development + production)
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

  // Função para exibir alertas temporários
  const showAlert = (message, type = "success") => {
    setAlert({ message, type })
    setTimeout(() => {
      setAlert(null)
    }, 6000)
  }

  // Carregar dados iniciais
  const fetchData = async () => {
    try {
      const resBarbers = await fetch(`${API_URL}/barbers`)
      if (!resBarbers.ok) throw new Error("Falha ao listar barbeiros")
      const dataBarbers = await resBarbers.json()
      setBarbers(dataBarbers)

      const resClients = await fetch(`${API_URL}/clients`)
      if (!resClients.ok) throw new Error("Falha ao listar clientes")
      const dataClients = await resClients.json()
      setClients(dataClients)

      const resAppointments = await fetch(`${API_URL}/appointments`)
      if (!resAppointments.ok) throw new Error("Falha ao listar agendamentos")
      const dataAppointments = await resAppointments.json()
      setAppointments(dataAppointments)
    } catch (error) {
      showAlert("Erro ao carregar dados do servidor. Certifique-se de que a API está rodando.", "error")
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  // Cadastrar Barbeiro
  const handleAddBarber = async (e) => {
    e.preventDefault()
    if (!newBarberName || !newBarberSpecialty) {
      showAlert("Por favor, preencha todos os campos do barbeiro.", "error")
      return
    }

    try {
      const response = await fetch(`${API_URL}/barbers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newBarberName, specialty: newBarberSpecialty })
      })

      if (response.ok) {
        const data = await response.json()
        showAlert(`Barbeiro "${data.name}" cadastrado com sucesso!`)
        setNewBarberName("")
        setNewBarberSpecialty("")
        fetchData()
      } else {
        const errData = await response.json()
        showAlert(`Erro ao cadastrar barbeiro: ${errData.detail || "Erro inesperado"}`, "error")
      }
    } catch (error) {
      showAlert("Erro de rede ao cadastrar barbeiro.", "error")
    }
  }

  // Cadastrar Cliente
  const handleAddClient = async (e) => {
    e.preventDefault()
    if (!newClientName || !newClientPhone) {
      showAlert("Por favor, preencha todos os campos do cliente.", "error")
      return
    }

    try {
      const response = await fetch(`${API_URL}/clients`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newClientName, phone: newClientPhone })
      })

      if (response.ok) {
        const data = await response.json()
        showAlert(`Cliente "${data.name}" cadastrado com sucesso!`)
        setNewClientName("")
        setNewClientPhone("")
        fetchData()
      } else {
        const errData = await response.json()
        showAlert(`Erro ao cadastrar cliente: ${errData.detail || "Erro inesperado"}`, "error")
      }
    } catch (error) {
      showAlert("Erro de rede ao cadastrar cliente.", "error")
    }
  }

  // Criar Agendamento (com validações de negócio)
  const handleBooking = async (e) => {
    e.preventDefault()
    if (!selectedBarberId || !selectedClientId || !bookingDate || !paymentMethod) {
      showAlert("Selecione barbeiro, cliente, data/hora e forma de pagamento.", "error")
      return
    }

    try {
      const response = await fetch(`${API_URL}/appointments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          barber_id: Number(selectedBarberId),
          client_id: Number(selectedClientId),
          date: bookingDate,
          payment_method: paymentMethod
        })
      })

      if (response.ok) {
        showAlert("Agendamento efetuado com sucesso!")
        setSelectedBarberId("")
        setSelectedClientId("")
        setBookingDate("")
        fetchData()
      } else {
        const errData = await response.json()
        // O backend retorna detail: string em caso de erros tratados
        const errorMessage = typeof errData.detail === "string"
          ? errData.detail
          : JSON.stringify(errData.detail) || "Conflito ou dados inválidos"
        showAlert(`Erro no Agendamento: ${errorMessage}`, "error")
      }
    } catch (error) {
      showAlert("Erro ao conectar com a API de agendamento.", "error")
    }
  }

  // Cancelar Agendamento
  const handleCancel = async (appointmentId) => {
    if (!window.confirm("Deseja realmente cancelar este agendamento?")) {
      return
    }

    try {
      const response = await fetch(`${API_URL}/appointments/${appointmentId}`, {
        method: "DELETE"
      })

      if (response.ok) {
        showAlert("Agendamento cancelado com sucesso!")
        fetchData()
      } else {
        showAlert("Erro ao tentar cancelar o agendamento.", "error")
      }
    } catch (error) {
      showAlert("Erro de rede ao cancelar agendamento.", "error")
    }
  }

  // Resolutores de nomes para exibição na lista
  const getBarberName = (id) => {
    const b = barbers.find((x) => x.id === id)
    return b ? b.name : `Barbeiro #${id}`
  }

  const getClientName = (id) => {
    const c = clients.find((x) => x.id === id)
    return c ? c.name : `Cliente #${id}`
  }

  const formatDateTime = (isoString) => {
    try {
      const d = new Date(isoString)
      return d.toLocaleString("pt-BR", {
        dateStyle: "short",
        timeStyle: "short"
      })
    } catch (e) {
      return isoString
    }
  }

  return (
    <div>
      <header>
        <h1>Barbearia <span>Premium</span></h1>
        <p className="subtitle">Marque seu Horário aqui</p>
      </header>

      {/* Pop-up de Alertas / Erros */}
      {alert && (
        <div className="alert-container">
          <div className={`alert alert-${alert.type}`}>
            <span>{alert.message}</span>
            <button className="alert-close" onClick={() => setAlert(null)}>&times;</button>
          </div>
        </div>
      )}

      {/* Painel de Estatísticas Rápidas */}
      <div className="stats-row">
        <div className="stat-box">
          <div className="stat-value">{barbers.length}</div>
          <div className="stat-label">Barbeiros</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{clients.length}</div>
          <div className="stat-label">Clientes</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{appointments.length}</div>
          <div className="stat-label">Agendados</div>
        </div>
      </div>

      {/* Painel do Dashboard em Grid */}
      <div className="dashboard-grid">

        {/* Coluna Lateral: Formulários de Cadastro */}
        <div className="col-sidebar">

          {/* Formulário: Agendar */}
          <div className="premium-card">
            <h2>
              Novo Agendamento
            </h2>
            <form onSubmit={handleBooking}>
              <div className="form-group">
                <label>Selecione seu Barbeiro</label>
                <select
                  value={selectedBarberId}
                  onChange={(e) => setSelectedBarberId(e.target.value)}
                >
                  <option value="">-- Escolha o Profissional --</option>
                  {barbers.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name} ({b.specialty})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Escolha o Cliente</label>
                <select
                  value={selectedClientId}
                  onChange={(e) => setSelectedClientId(e.target.value)}
                >
                  <option value="">-- Escolha o Cliente --</option>
                  {clients.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Data e Horário</label>
                <input
                  type="datetime-local"
                  value={bookingDate}
                  onChange={(e) => setBookingDate(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Forma de Pagamento</label>
                <select
                  value={paymentMethod}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                >
                  <option value="Cartão de Crédito">Cartão de Crédito</option>
                  <option value="Cartão de Débito">Cartão de Débito</option>
                  <option value="Dinheiro">Dinheiro</option>
                  <option value="Pix">Pix</option>
                </select>
              </div>

              <button className="btn-primary" type="submit">
                Confirmar Agendamento
              </button>
            </form>
          </div>

          {/* Formulário: Cadastrar Barbeiro */}
          <div className="premium-card">
            <h2>
              Cadastrar Barbeiro
            </h2>
            <form onSubmit={handleAddBarber}>
              <div className="form-group">
                <label>Nome do Barbeiro</label>
                <input
                  type="text"
                  placeholder="Ex: Nome do barbeiro"
                  value={newBarberName}
                  onChange={(e) => setNewBarberName(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Especialidade</label>
                <input
                  type="text"
                  placeholder="Ex: Barba & Navalha"
                  value={newBarberSpecialty}
                  onChange={(e) => setNewBarberSpecialty(e.target.value)}
                />
              </div>
              <button className="btn-primary" type="submit">
                Adicionar Barbeiro
              </button>
            </form>
          </div>

          {/* Formulário: Cadastrar Cliente */}
          <div className="premium-card">
            <h2>
              Cadastrar Cliente
            </h2>
            <form onSubmit={handleAddClient}>
              <div className="form-group">
                <label>Nome do Cliente</label>
                <input
                  type="text"
                  placeholder="Ex: João da Silva"
                  value={newClientName}
                  onChange={(e) => setNewClientName(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Telefone</label>
                <input
                  type="tel"
                  placeholder="Ex: (31) 91234-5678"
                  value={newClientPhone}
                  onChange={(e) => setNewClientPhone(e.target.value)}
                />
              </div>
              <button className="btn-primary" type="submit">
                Adicionar Cliente
              </button>
            </form>
          </div>

        </div>

        {/* Coluna Principal: Listas de Agendamentos e Cadastros */}
        <div className="col-main">

          {/* Lista de Agendamentos Ativos */}
          <div className="premium-card">
            <h2>
              Agenda Ativa
            </h2>
            {appointments.length === 0 ? (
              <div className="empty-state">Nenhum agendamento marcado no momento.</div>
            ) : (
              <div className="appointments-grid">
                {appointments.map((appt) => (
                  <div key={appt.id} className="appointment-card">
                    <div className="appt-details">
                      <div className="appt-time">{formatDateTime(appt.date)}</div>
                      <div className="appt-people">
                        <strong>Cliente:</strong> {getClientName(appt.client_id)} <br />
                        <strong>Barbeiro:</strong> {getBarberName(appt.barber_id)}
                      </div>
                      <div className="appt-payment">
                        Pagamento: {appt.payment_method}
                      </div>
                    </div>
                    <button
                      className="btn-danger-sm"
                      onClick={() => handleCancel(appt.id)}
                    >
                      Cancelar
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Lista de Barbeiros */}
          <div className="premium-card">
            <h2>
              Nossos Profissionais
            </h2>
            {barbers.length === 0 ? (
              <div className="empty-state">Nenhum barbeiro cadastrado ainda.</div>
            ) : (
              <ul className="custom-list">
                {barbers.map((b) => (
                  <li key={b.id} className="list-item">
                    <div className="item-info">
                      <span className="item-title">{b.name}</span>
                      <span className="item-subtitle">ID: {b.id} • {b.specialty}</span>
                    </div>
                    <span className="badge badge-gold">Disponível</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Lista de Clientes */}
          <div className="premium-card">
            <h2>
              Clientes Cadastrados
            </h2>
            {clients.length === 0 ? (
              <div className="empty-state">Nenhum cliente cadastrado ainda.</div>
            ) : (
              <ul className="custom-list">
                {clients.map((c) => (
                  <li key={c.id} className="list-item">
                    <div className="item-info">
                      <span className="item-title">{c.name}</span>
                      <span className="item-subtitle">ID: {c.id} • Contato: {c.phone}</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

        </div>

      </div>
    </div>
  )
}

export default App