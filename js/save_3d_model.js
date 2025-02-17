// js/save_3d_model.js
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "Comfy.SaveAndPreview3DModel",
    async setup() {
        // 3Dプレビューダイアログを作成
        const createPreviewDialog = (modelData, filename) => {
            console.log(`createPreviewDialog called. filename: ${filename}`); // DEBUG 1
            console.log(`modelData length: ${modelData.length}`); // DEBUG 2

            // Three.jsのスクリプトを動的に読み込み
            const loadThreeJS = async () => {
                if (window.THREE) {
                    console.log("Three.js already loaded."); // DEBUG 3
                    return;
                }

                try {
                    await Promise.all([
                        // Three.jsのコアライブラリ
                        new Promise((resolve) => {
                            const script = document.createElement('script');
                            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
                            script.onload = () => {
                                console.log("Three.js core loaded."); // DEBUG 4
                                resolve();
                            };
                            script.onerror = (error) => {  // エラーハンドリングを追加
                                console.error("Error loading Three.js core:", error);
                                resolve(); // エラーでもresolveして続行
                            }
                            document.head.appendChild(script);
                        }),
                        // GLTFローダー
                        new Promise((resolve) => {
                            const script = document.createElement('script');
                            script.src = 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js';
                            script.onload = () => {
                                console.log("GLTFLoader loaded.");  // DEBUG 5
                                resolve();
                            }
                            script.onerror = (error) => { // エラーハンドリングを追加
                                console.error("Error loading GLTFLoader:", error);
                                resolve();
                            }
                            document.head.appendChild(script);
                        }),
                        // OrbitControls
                        new Promise((resolve) => {
                            const script = document.createElement('script');
                            script.src = 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js';
                            script.onload = () => {
                                console.log("OrbitControls loaded."); // DEBUG 6
                                resolve();
                            };
                            script.onerror = (error) => { // エラーハンドリングを追加
                                console.error("Error loading OrbitControls:", error);
                                resolve();
                            }
                            document.head.appendChild(script);
                        })
                    ]);
                    console.log("All Three.js scripts loaded.");  // DEBUG 7
                } catch (error) {
                    console.error("Error loading Three.js scripts:", error); // DEBUG 8
                }
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
                console.log("Scene created.");  // DEBUG 9

                const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
                camera.position.z = 5;
                console.log("Camera created."); // DEBUG 10

                const renderer = new THREE.WebGLRenderer();
                renderer.setSize(container.clientWidth, container.clientHeight);
                container.appendChild(renderer.domElement);
                console.log("Renderer created and added to container."); // DEBUG 11

                // ライトの追加
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
                scene.add(ambientLight);
                const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
                directionalLight.position.set(0, 1, 0);
                scene.add(directionalLight);
                console.log("Lights added."); // DEBUG 12

                // OrbitControlsの設定
                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                console.log("OrbitControls created.");  // DEBUG 13

                // GLBファイルを読み込み
                const loader = new THREE.GLTFLoader();
                console.log("GLTFLoader created."); // DEBUG 14

                // 重要: latin1でエンコードされた文字列からUint8Arrayを作成
                const uint8Array = new Uint8Array([...modelData].map(char => char.charCodeAt(0)));
                console.log(`Uint8Array created. Length: ${uint8Array.length}`);  // DEBUG 15
                const modelBlob = new Blob([uint8Array], { type: 'model/gltf-binary' });
                console.log("Blob created."); // DEBUG 16
                const modelUrl = URL.createObjectURL(modelBlob);
                console.log("modelUrl created."); // DEBUG 17

                loader.load(modelUrl, (gltf) => {
                    console.log("GLTF model loaded."); // DEBUG 18
                    scene.add(gltf.scene);
                    console.log("GLTF scene added to the scene."); // DEBUG 19

                    // モデルを中央に配置
                    const box = new THREE.Box3().setFromObject(gltf.scene);
                    const center = box.getCenter(new THREE.Vector3());
                    gltf.scene.position.sub(center);

                    // カメラ位置の自動調整
                    const size = box.getSize(new THREE.Vector3());
                    const maxDim = Math.max(size.x, size.y, size.z);
                    camera.position.z = maxDim * 2;

                    URL.revokeObjectURL(modelUrl); // Blob URLを解放
                    console.log("modelUrl revoked."); // DEBUG 20
                },
                (xhr) => { // プログレスイベントのハンドラを追加
                  console.log((xhr.loaded / xhr.total * 100) + '% loaded'); // DEBUG 21
                },
                (error) => { // エラーイベントのハンドラを追加
                  console.error('An error happened during loading:', error); // DEBUG 22
                });

                // アニメーションループ
                function animate() {
                    requestAnimationFrame(animate);
                    controls.update();
                    renderer.render(scene, camera);
                }
                animate();
                console.log("Animation loop started."); // DEBUG 23

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
            console.log("Dialog shown."); // DEBUG 24
            initThreeJS();
        };

        // プレビューメッセージのハンドラーを登録
        api.addEventListener("preview_3d_model", ({ detail }) => {
            console.log("preview_3d_model event received:", detail);  // DEBUG 25
            createPreviewDialog(detail.model_data, detail.filename);
        });
    }
});