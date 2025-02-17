import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "Comfy.SaveAndPreview3DModel",
    async setup() {
        // 3Dプレビューダイアログを作成
        const createPreviewDialog = (modelData, filename) => {
            // Three.jsのスクリプトを動的に読み込み
            const loadThreeJS = async () => {
                if (window.THREE) return;

                await Promise.all([
                    // Three.jsのコアライブラリ
                    new Promise((resolve) => {
                        const script = document.createElement('script');
                        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
                        script.onload = resolve;
                        document.head.appendChild(script);
                    }),
                    // GLTFローダー
                    new Promise((resolve) => {
                        const script = document.createElement('script');
                        script.src = 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js';
                        script.onload = resolve;
                        document.head.appendChild(script);
                    }),
                    // OrbitControls
                    new Promise((resolve) => {
                        const script = document.createElement('script');
                        script.src = 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js';
                        script.onload = resolve;
                        document.head.appendChild(script);
                    })
                ]);
            };

            // ダイアログを作成
            const dialog = document.createElement('dialog');
            dialog.style.cssText = `
                width: 800px;
                height: 600px;
                padding: 20px;
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 5px;
                color: white;
            `;

            // タイトルバー
            const titleBar = document.createElement('div');
            titleBar.style.cssText = `
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            `;
            const title = document.createElement('h3');
            title.textContent = `3D Preview: ${filename}`;
            title.style.margin = '0';
            
            const closeButton = document.createElement('button');
            closeButton.textContent = '×';
            closeButton.style.cssText = `
                background: none;
                border: none;
                color: white;
                font-size: 20px;
                cursor: pointer;
            `;
            closeButton.onclick = () => dialog.close();
            
            titleBar.appendChild(title);
            titleBar.appendChild(closeButton);

            // 3Dビューアーのコンテナ
            const container = document.createElement('div');
            container.style.cssText = `
                width: 100%;
                height: 500px;
                background: #2a2a2a;
                border-radius: 5px;
            `;

            dialog.appendChild(titleBar);
            dialog.appendChild(container);
            document.body.appendChild(dialog);

            // Three.jsのセットアップ
            const initThreeJS = async () => {
                await loadThreeJS();

                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x2a2a2a);

                const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
                camera.position.z = 5;

                const renderer = new THREE.WebGLRenderer();
                renderer.setSize(container.clientWidth, container.clientHeight);
                container.appendChild(renderer.domElement);

                // ライトの追加
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
                scene.add(ambientLight);
                const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
                directionalLight.position.set(0, 1, 0);
                scene.add(directionalLight);

                // OrbitControlsの設定
                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;

                // GLBファイルを読み込み
                const loader = new THREE.GLTFLoader();
                const modelBlob = new Blob([Uint8Array.from(atob(modelData), c => c.charCodeAt(0))], { type: 'model/gltf-binary' });
                const modelUrl = URL.createObjectURL(modelBlob);

                loader.load(modelUrl, (gltf) => {
                    scene.add(gltf.scene);

                    // モデルを中央に配置
                    const box = new THREE.Box3().setFromObject(gltf.scene);
                    const center = box.getCenter(new THREE.Vector3());
                    gltf.scene.position.sub(center);

                    // カメラ位置の自動調整
                    const size = box.getSize(new THREE.Vector3());
                    const maxDim = Math.max(size.x, size.y, size.z);
                    camera.position.z = maxDim * 2;
                    
                    URL.revokeObjectURL(modelUrl);
                });

                // アニメーションループ
                function animate() {
                    requestAnimationFrame(animate);
                    controls.update();
                    renderer.render(scene, camera);
                }
                animate();

                // ウィンドウリサイズ対応
                window.addEventListener('resize', () => {
                    camera.aspect = container.clientWidth / container.clientHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(container.clientWidth, container.clientHeight);
                });
            };

            dialog.addEventListener('click', (e) => {
                if (e.target === dialog) {
                    dialog.close();
                }
            });

            // ダイアログを表示してThree.jsを初期化
            dialog.showModal();
            initThreeJS();
        };

        // プレビューメッセージのハンドラーを登録
        api.addEventListener("preview_3d_model", ({ detail }) => {
            createPreviewDialog(detail.model_data, detail.filename);
        });
    }
});