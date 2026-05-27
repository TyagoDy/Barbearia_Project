def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-ID" in response.headers


def test_create_and_read_barber(client):
    response = client.post(
        "/barbers",
        json={"name": "Sweeney Todd", "specialty": "Razor Shaves"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Sweeney Todd"
    assert "id" in data
    
    get_response = client.get("/barbers")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 1

def test_create_and_read_client(client):
    response = client.post(
        "/clients",
        json={"name": "John Doe", "phone": "123456789"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert "id" in data
    
    get_response = client.get("/clients")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 1

def test_create_appointment_success(client):
    # Criar Barbeiro
    res_b = client.post("/barbers", json={"name": "Barber A", "specialty": "Haircut"})
    b_id = res_b.json()["id"]
    
    # Criar Cliente
    res_c = client.post("/clients", json={"name": "Client A", "phone": "99999"})
    c_id = res_c.json()["id"]
    
    # Criar Agendamento
    res_a = client.post(
        "/appointments",
        json={
            "barber_id": b_id,
            "client_id": c_id,
            "date": "2026-05-26T10:00:00",
            "payment_method": "Pix"
        }
    )
    assert res_a.status_code == 200
    appt = res_a.json()
    assert appt["barber_id"] == b_id
    assert appt["client_id"] == c_id
    assert appt["payment_method"] == "Pix"

def test_create_appointment_barber_not_found(client):
    # Criar Cliente
    res_c = client.post("/clients", json={"name": "Client A", "phone": "99999"})
    c_id = res_c.json()["id"]
    
    # Criar Agendamento com barbeiro inexistente
    res_a = client.post(
        "/appointments",
        json={
            "barber_id": 999,
            "client_id": c_id,
            "date": "2026-05-26T10:00:00",
            "payment_method": "Pix"
        }
    )
    assert res_a.status_code == 404
    assert "Barber not found" in res_a.json()["detail"]

def test_create_appointment_client_not_found(client):
    # Criar Barbeiro
    res_b = client.post("/barbers", json={"name": "Barber A", "specialty": "Haircut"})
    b_id = res_b.json()["id"]
    
    # Criar Agendamento com cliente inexistente
    res_a = client.post(
        "/appointments",
        json={
            "barber_id": b_id,
            "client_id": 999,
            "date": "2026-05-26T10:00:00",
            "payment_method": "Pix"
        }
    )
    assert res_a.status_code == 404
    assert "Client not found" in res_a.json()["detail"]

def test_create_appointment_conflict(client):
    # Criar Barbeiro
    res_b = client.post("/barbers", json={"name": "Barber A", "specialty": "Haircut"})
    b_id = res_b.json()["id"]
    
    # Criar Clientes
    res_c1 = client.post("/clients", json={"name": "Client A", "phone": "99999"})
    c1_id = res_c1.json()["id"]
    res_c2 = client.post("/clients", json={"name": "Client B", "phone": "88888"})
    c2_id = res_c2.json()["id"]
    
    # Agendamento 1
    res_a1 = client.post(
        "/appointments",
        json={
            "barber_id": b_id,
            "client_id": c1_id,
            "date": "2026-05-26T10:00:00",
            "payment_method": "Pix"
        }
    )
    assert res_a1.status_code == 200
    
    # Agendamento 2 (Mesmo barbeiro, mesmo horário -> Conflito)
    res_a2 = client.post(
        "/appointments",
        json={
            "barber_id": b_id,
            "client_id": c2_id,
            "date": "2026-05-26T10:00:00",
            "payment_method": "Dinheiro"
        }
    )
    assert res_a2.status_code == 409
    assert "already booked" in res_a2.json()["detail"]

def test_delete_appointment(client):
    # Criar Barbeiro e Cliente
    res_b = client.post("/barbers", json={"name": "Barber A", "specialty": "Haircut"})
    b_id = res_b.json()["id"]
    res_c = client.post("/clients", json={"name": "Client A", "phone": "99999"})
    c_id = res_c.json()["id"]
    
    # Agendamento
    res_a = client.post(
        "/appointments",
        json={
            "barber_id": b_id,
            "client_id": c_id,
            "date": "2026-05-26T10:00:00",
            "payment_method": "Pix"
        }
    )
    appt_id = res_a.json()["id"]
    
    # Exclusão
    res_del = client.delete(f"/appointments/{appt_id}")
    assert res_del.status_code == 200
    assert res_del.json() == {"message": "Appointment deleted"}
    
    # Validar que foi removido da lista
    res_list = client.get("/appointments")
    assert len(res_list.json()) == 0


def test_delete_appointment_not_found(client):
    response = client.delete("/appointments/9999")
    assert response.status_code == 200
    assert response.json() == {"message": "Appointment not found"}
