package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"

	protocol "github.com/maksimkasimovhse/httpPractice"
)

func main() {
	User := protocol.UserRequest{ID: "1", Name: "Temirlan"}
	jsonData, _ := json.Marshal(User)

	req, err := http.NewRequest("POST", "http://localhost:8080/hello", bytes.NewBuffer(jsonData))
	if err != nil {
		fmt.Printf("Ошибка создания запроса: %v\n", err)
		return
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Auth-Token", "secret")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("Ошибка передачи данных: %v\n", err)
		return
	}

	defer resp.Body.Close()

	var serverResponse protocol.UserResponse
	err = json.NewDecoder(resp.Body).Decode(&serverResponse)
	if err != nil {
		fmt.Printf("Ошибка декодирования ответа: %v\n", err)
	}

	fmt.Printf("Статус: %s\n", serverResponse.Status)
	fmt.Printf("Сообщение: %s\n", serverResponse.Message)
}
