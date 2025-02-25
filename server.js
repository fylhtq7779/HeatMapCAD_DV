const express = require('express');
const fileUpload = require('express-fileupload');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));
app.use(fileUpload());

// Хранилище для загружаемых файлов
const uploads = new Map();
const UPLOAD_DIR = path.join(__dirname, 'uploads');

// Создаем директорию для загрузок, если её нет
if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR);
}

// Инициализация загрузки файла
app.post('/api/heatmap/init', (req, res) => {
    const { filename, size } = req.body;
    const uploadId = uuidv4();
    
    uploads.set(uploadId, {
        filename,
        size,
        chunks: new Map(),
        completed: false
    });

    res.json({ upload_id: uploadId });
});

// Загрузка чанка файла
app.post('/api/heatmap/chunk', (req, res) => {
    if (!req.files || !req.files.chunk) {
        return res.status(400).send('No chunk uploaded');
    }

    const { upload_id, chunk_number } = req.body;
    const upload = uploads.get(upload_id);

    if (!upload) {
        return res.status(404).send('Upload not found');
    }

    const chunk = req.files.chunk;
    upload.chunks.set(parseInt(chunk_number), chunk.data);

    res.send('Chunk received');
});

// Завершение загрузки файла
app.post('/api/heatmap/finish', async (req, res) => {
    const { upload_id } = req.body;
    const upload = uploads.get(upload_id);

    if (!upload) {
        return res.status(404).send('Upload not found');
    }

    try {
        // Собираем файл из чанков
        const chunks = Array.from(upload.chunks.entries())
            .sort(([a], [b]) => a - b)
            .map(([_, chunk]) => chunk);

        const finalBuffer = Buffer.concat(chunks);
        const filePath = path.join(UPLOAD_DIR, `${upload_id}.json`);
        
        await fs.promises.writeFile(filePath, finalBuffer);
        
        // Очищаем память
        upload.chunks.clear();
        upload.completed = true;

        res.json({
            id: upload_id,
            filename: upload.filename,
            size: finalBuffer.length
        });
    } catch (error) {
        console.error('Error finishing upload:', error);
        res.status(500).send('Error finishing upload');
    }
});

// Получение списка тепловых карт
app.get('/api/heatmap/list', async (req, res) => {
    try {
        const files = await fs.promises.readdir(UPLOAD_DIR);
        const heatmaps = await Promise.all(
            files.map(async (file) => {
                const stats = await fs.promises.stat(path.join(UPLOAD_DIR, file));
                return {
                    id: path.parse(file).name,
                    size: stats.size,
                    created: stats.birthtime
                };
            })
        );
        res.json(heatmaps);
    } catch (error) {
        console.error('Error listing heatmaps:', error);
        res.status(500).send('Error listing heatmaps');
    }
});

// Получение данных тепловой карты
app.get('/api/heatmap/:id', async (req, res) => {
    const { id } = req.params;
    const filePath = path.join(UPLOAD_DIR, `${id}.json`);

    try {
        const data = await fs.promises.readFile(filePath, 'utf8');
        res.json(JSON.parse(data));
    } catch (error) {
        console.error('Error reading heatmap:', error);
        res.status(404).send('Heatmap not found');
    }
});

// Обновляем index.html для отображения тепловых карт
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Запуск сервера
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
}); 