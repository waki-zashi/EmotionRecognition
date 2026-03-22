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

	resp, err := http.Post("http://localhost:8080/hello", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		fmt.Printf("Ошибка передачи данных: %v\n", err)
		return
	}
		

	var serverResponse protocol.UserResponse
	err = json.NewDecoder(resp.Body).Decode(&serverResponse)
	if err != nil {
		fmt.Printf("Ошибка декодирования ответа: %v\n", err)
	}

	fmt.Printf("Статус: %s\n", serverResponse.Status)
	fmt.Printf("Сообщение: %s\n", serverResponse.Message)
}
