package main

import (
	"encoding/json"
	"fmt"
	"net/http"

	protocol "github.com/maksimkasimovhse/httpPractice"
)

func myHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		fmt.Fprint(w, "Вы хотите получить данные по запросу (GET)")
	case http.MethodPost:
		var NewMessage protocol.UserRequest
		err := json.NewDecoder(r.Body).Decode(&NewMessage)
		if err != nil {
			fmt.Printf("Ошибка декодирования: %v", err)
			return
		}
		fmt.Printf("Имя пользователя: %s, ID: %s\n", NewMessage.Name, NewMessage.ID)

		ServerResponse := protocol.UserResponse{Message: fmt.Sprintf("Привет, %s! Твой ID %s успешно обработан", NewMessage.Name, NewMessage.ID), Status: "Успешно"}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		err = json.NewEncoder(w).Encode(ServerResponse)
		if err != nil {
			fmt.Printf("Ошибка отправки: %v", err)
		}

	default:
		fmt.Fprint(w, "Такой метод не поддерживается")
	}
}

func main() {
	http.HandleFunc("/hello", myHandler)
	fmt.Println("Сервер ждет запроса на порту: 8080...")

	http.ListenAndServe(":8080", nil)
}
