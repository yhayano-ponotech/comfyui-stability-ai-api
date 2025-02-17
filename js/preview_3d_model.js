import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "Comfy.Preview3DModel", // name属性を変更
    async setup() {
        // 3Dプレビューダイアログを作成
        const createPreviewDialog = (arrayBuffer, filename, fileType) => {

            // Three.jsのスクリプトを動的に読み込み
            const loadThreeJS = async () => {
                if (window.THREE) return;
                await Promise.all([
                    // Three.jsのコアライブラリ
                    import('https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js'),
                    import('https://cdn.jsdelivr.net/npm/three@0.164.1/examples/jsm/controls/OrbitControls.js'),
                ]).then(values => {
                    const [THREE_] = values;
                    window.THREE = THREE_;
                }).catch(error => {
                    console.error('Error loading Three.js modules:', error);
                });
            };

            // 必要なローダーを動的にロード
            const loadLoaders = async (fileType) => {
                if (fileType === 'obj' && !window.OBJLoader) {
                    const { OBJLoader } = await import('https://cdn.jsdelivr.net/npm/three@0.164.1/examples/jsm/loaders/OBJLoader.js');
                    window.OBJLoader = OBJLoader;
                }
                if (fileType === 'obj' && !window.MTLLoader) {
                    const { MTLLoader } = await import('https://cdn.jsdelivr.net/npm/three@0.164.1/examples/jsm/loaders/MTLLoader.js');
                    window.MTLLoader = MTLLoader;
                }

                if (fileType === 'glb' && !window.GLTFLoader) {
                    const { GLTFLoader } = await import('https://cdn.jsdelivr.net/npm/three@0.164.1/examples/jsm/loaders/GLTFLoader.js');
                    window.GLTFLoader = GLTFLoader;
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
            title.textContent = `3D Preview`; // タイトルからファイル名表示を削除
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
                await loadThreeJS();  // Three.jsのコアをロード
                await loadLoaders(fileType);

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

                const modelBlob = new Blob([modelData], { type: 'application/octet-stream' });
                const modelUrl = URL.createObjectURL(modelBlob);


                // GLTF/GLBファイルの読み込み
                if (fileType === "glb") {
                    const loader = new window.GLTFLoader();
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
                        animate(); // アニメーション開始
                    }, undefined, function (error) {
                        console.error('An error happened during the loading of the GLTF/GLB model:', error);
                        dialog.close();
                    });
                } else if (fileType === 'obj') {
                    const loader = new window.OBJLoader();
                    // MTLローダーのインスタンスを作成
                    const mtlLoader = new window.MTLLoader();
                    // マテリアルをロード
                    mtlLoader.load( 'http://localhost:8188/viewfile?filepath=C:\\Users\\User\\Desktop\\ai\\ComfyUI_windows_portable\\ComfyUI\\custom_nodes\\comfyui-stability-ai-api\\examples\\output\\output.mtl', function( materials ) {
                            materials.preload();

                            // OBJローダーにマテリアルを設定
                            loader.setMaterials( materials );
                            loadOBJ(loader,modelUrl,scene,camera);

                        },
                        // called when loading has errors
                        function ( error ) {
                            console.log( '[MTL Loader] An error happened:' + error );
                            console.log( '[MTL Loader] Try to load obj without mtl.' );
                            loadOBJ(loader,modelUrl,scene,camera); //mtlロードでエラーが出たら、mtlなしでobjをロード
                        }
                    );
                } else if (fileType === 'ply'){
                    const { PLYLoader } = await import('https://cdn.jsdelivr.net/npm/three@0.164.1/examples/jsm/loaders/PLYLoader.js');
                    const loader = new PLYLoader();
                    loader.load(modelUrl, function (geometry) {
                        geometry.computeVertexNormals();
                        const material = new THREE.MeshStandardMaterial({ color: 0x0055ff, flatShading: true });
                        const mesh = new THREE.Mesh(geometry, material);

                        // モデルを中央に配置
                        const box = new THREE.Box3().setFromObject(mesh);
                        const center = box.getCenter(new THREE.Vector3());
                        mesh.position.sub(center);

                        // カメラ位置の自動調整
                        const size = box.getSize(new THREE.Vector3());
                        const maxDim = Math.max(size.x, size.y, size.z);
                        camera.position.z = maxDim * 2;

                        scene.add(mesh);
                        URL.revokeObjectURL(modelUrl);
                        animate();
                    }, undefined, function (error) {
                        console.error('An error happened during the loading of the PLY model:', error);
                        dialog.close();
                    });

                }
                // アニメーションループ
                function animate() {
                    requestAnimationFrame(animate);
                    controls.update();
                    renderer.render(scene, camera);
                }
                
                //objをロード(mtlのロードが失敗した場合も呼ばれる)
                function loadOBJ(loader,modelUrl,scene,camera){
                    // OBJファイルをロード
                    loader.load( modelUrl, function ( object ) {
                        scene.add( object );
                        // モデルを中央に配置
                        const box = new THREE.Box3().setFromObject(object);
                        const center = box.getCenter(new THREE.Vector3());
                        object.position.sub(center);

                        // カメラ位置の自動調整
                        const size = box.getSize(new THREE.Vector3());
                        const maxDim = Math.max(size.x, size.y, size.z);
                        camera.position.z = maxDim * 2;
                        animate(); // アニメーション開始
                    }, undefined, function ( error ) {
                        console.error( 'An error happened during the loading of the OBJ model:', error );
                        dialog.close();
                    } );
                }


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

        // プレビューメッセージのハンドラーを登録（イベント名と引数を修正）
        api.addEventListener("preview_3d_model", (event) => { //イベント名を変更
            const { model_data, filename, model_type } = event.detail;

            // modelData を ArrayBuffer に変換
            const uint8Array = new Uint8Array(model_data);
            const arrayBuffer = uint8Array.buffer;
            createPreviewDialog(arrayBuffer, filename, model_type.toLowerCase()); //ArrayBufferを渡す
        });

    }
});