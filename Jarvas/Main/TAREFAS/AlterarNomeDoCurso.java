package TAREFAS;
import java.awt.AWTException;
import java.awt.Robot;
import java.awt.event.KeyEvent;

public class AlterarNomeDoCurso {
    
    private static Robot robot;
    // F10
    static {
        try {
            robot = new Robot();
            // Configurações equivalentes às do pyautogui
            robot.setAutoDelay(100); // PAUSE = 0.1 segundos (100ms)
            // FAILSAFE = true (não tem equivalente exato no Robot, mas pode ser implementado)
        } catch (AWTException e) {
            System.err.println("Erro ao inicializar o Robot: " + e.getMessage());
        }
    }
    
    /** Função principal para executar o bot de nome do curso */
    public static void executarBotCurso() {
        try {
            timeSleep(5000);

            pressKey(KeyEvent.VK_ENTER);
            timeSleep(1000);

            pressKey(KeyEvent.VK_TAB);
            timeSleep(1000);

            hotkey(KeyEvent.VK_CONTROL, KeyEvent.VK_V);
            timeSleep(1000);

            for (int i = 0; i < 28; i++) {
                pressKey(KeyEvent.VK_TAB);
            }
            timeSleep(1000);

            for (int i = 0; i < 2; i++) {
                pressKey(KeyEvent.VK_ENTER);
            }
            timeSleep(1000);

            pressKey(KeyEvent.VK_DOWN);
            timeSleep(1000);
            
        } catch (Exception e) {
            System.err.println("Erro na execução do bot: " + e.getMessage());
        }
    }
    
    // Métodos auxiliares
    private static void timeSleep(int milliseconds) {
        try {
            Thread.sleep(milliseconds);
        } catch (InterruptedException e) {
            System.err.println("Thread interrompida: " + e.getMessage());
        }
    }
    
    private static void pressKey(int keyCode) {
        robot.keyPress(keyCode);
        robot.keyRelease(keyCode);
    }
    
    private static void hotkey(int key1, int key2) {
        robot.keyPress(key1);
        robot.keyPress(key2);
        robot.keyRelease(key2);
        robot.keyRelease(key1);
    }
    
    // FAILSAFE implementation (para simular o FAILSAFE do pyautogui)
    private static void setupFailsafe() {
        Thread failsafeThread = new Thread(() -> {
            try {
                while (true) {
                    // Verifica se o mouse está no canto superior esquerdo
                    if (java.awt.MouseInfo.getPointerInfo().getLocation().x == 0 && 
                        java.awt.MouseInfo.getPointerInfo().getLocation().y == 0) {
                        System.out.println("FAILSAFE ativado! Encerrando...");
                        System.exit(0);
                    }
                    Thread.sleep(100);
                }
            } catch (Exception e) {
                System.err.println("Erro no FAILSAFE: " + e.getMessage());
            }
        });
        failsafeThread.setDaemon(true);
        failsafeThread.start();
    }
    
    // Executar apenas se chamado diretamente
    public static void main(String[] args) {
        // Ativar FAILSAFE (opcional)
        setupFailsafe();
        
        executarBotCurso();
    }
}