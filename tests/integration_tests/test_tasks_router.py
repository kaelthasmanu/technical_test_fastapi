def test_tasks_crud_flow(client):
    # sign up and sign in to get token
    r = client.post("/api/v2/auth/sign-up", json={"email": "user@tasks.com", "password": "pass", "name": "u"})
    assert r.status_code == 200
    r = client.post("/api/v2/auth/sign-in", json={"email__eq": "user@tasks.com", "password": "pass"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # create task
    r = client.post(
        "/api/v1/tasks",
        json={"titulo": "t1", "descripcion": "d1", "estado": "pendiente"},
        headers=headers,
    )
    assert r.status_code == 201
    task = r.json()
    task_id = task["id"]
    assert task["titulo"] == "t1"

    # list tasks (should contain our task)
    r = client.get("/api/v1/tasks", headers=headers)
    assert r.status_code == 200
    tasks = r.json()
    assert any(t["id"] == task_id for t in tasks)

    # get task by id
    r = client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["id"] == task_id

    # update task
    r = client.put(
        f"/api/v1/tasks/{task_id}",
        json={"titulo": "t1-upd", "estado": "completada"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["titulo"] == "t1-upd"
    assert r.json()["estado"] == "completada"

    # delete task
    r = client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
    assert r.status_code == 204

    # get after delete should 404
    r = client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert r.status_code == 404
