package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/google/uuid"
	"github.com/redis/go-redis/v9"
)

var rdb *redis.Client

func authMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {

		token := r.Header.Get("X-Auth-Token")

		if token != "secret" {
			fmt.Println("Пользователь без пароля пытается отправить данные")
			w.WriteHeader(http.StatusForbidden)
			fmt.Fprint(w, "Доступ запрещен: неверный или пустой токен")
			return
		}

		next(w, r)
	}

}

func corsMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {

		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, X-Auth-Token")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusOK)
			return
		}
		next(w, r)
	}
}

func myHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodPost:

		r.ParseMultipartForm(5 << 20)

		file, header, err := r.FormFile("image")
		if err != nil {
			http.Error(w, "Ошибка получения файла", http.StatusBadRequest)
			return
		}
		defer file.Close()

		fmt.Printf("Пришел файл с параметрами:\n Размер: %d, Название: %s\n", header.Size, header.Filename)

		fileBytes, err := io.ReadAll(file)
		if err != nil {
			http.Error(w, "Ошибка чтения файла", http.StatusInternalServerError)
			return
		}

		ctx := r.Context()
		taskID := uuid.New().String()

		imageData64 := base64.StdEncoding.EncodeToString(fileBytes)

		task := ImageTask{
			TaskID:    taskID,
			UserID:    101,
			FileName:  header.Filename,
			ImageData: imageData64,
		}

		taskJSON, err := json.Marshal(task)
		if err != nil {
			http.Error(w, "Ошибка маршалинга JSON", http.StatusInternalServerError)
			return
		}

		err = rdb.LPush(ctx, "image_tasks", taskJSON).Err()
		if err != nil {
			fmt.Printf("Ошибка Redis: %v\n", err)
			http.Error(w, "Ошибка записи в очередь", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusAccepted)
		fmt.Fprintf(w, `{"status": "accepted", "task_id": "%s"}`, taskID)

	default:
		fmt.Fprint(w, "Такой метод не поддерживается")
	}
}

func statusHandler(w http.ResponseWriter, r *http.Request) {
	taskID := r.URL.Query().Get("id")
	if taskID == "" {
		http.Error(w, "параметр ID не дошел", http.StatusBadRequest)
		return
	}

	ctx := r.Context()

	val, err := rdb.Get(ctx, "result:"+taskID).Result()

	if err == redis.Nil {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"task_id": "%s", "status": "processing"}`, taskID)
		return
	} else if err != nil {
		http.Error(w, "Ошибка Redis", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	fmt.Fprint(w, val)
}

func main() {
	redisAddr := os.Getenv("REDIS_ADDR")

	if redisAddr == "" {
		redisAddr = "localhost:6379"
	}

	rdb = redis.NewClient(&redis.Options{
		Addr: redisAddr,
	})

	http.HandleFunc("/hello", corsMiddleware(authMiddleware(myHandler)))
	http.HandleFunc("/status", corsMiddleware(statusHandler))

	fmt.Println("Сервер ждет запроса на порту: 8080...")
	http.ListenAndServe(":8080", nil)
}
