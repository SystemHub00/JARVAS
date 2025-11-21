package TAREFAS;
import java.awt.AWTException;
import java.awt.Robot;
import java.awt.event.KeyEvent;
import java.awt.datatransfer.Clipboard;
import java.awt.datatransfer.DataFlavor;
import java.awt.datatransfer.StringSelection;
import java.awt.Toolkit;

public class IncluirEmTurma {
    
    private static Robot robot;
    // CHROME
    // F10
    static {
        try {
            robot = new Robot();
        } catch (AWTException e) {
            System.err.println("Erro ao inicializar o Robot: " + e.getMessage());
        }
    }
    
    /** Função principal para incluir em turma */
    public static void executarIncluirTurma() {
        try {
            timeSleep(5000);
            int c = 0;
            
            while (true) { 
                c++;
                hotkey(KeyEvent.VK_CONTROL, KeyEvent.VK_C);
                timeSleep(1000);
                
                hotkey(KeyEvent.VK_ALT, KeyEvent.VK_TAB);
                timeSleep(1000);
                
                pressKey(KeyEvent.VK_F4);
                timeSleep(1000);
                
                pressKey(KeyEvent.VK_TAB);
                timeSleep(1000);
                
                hotkey(KeyEvent.VK_CONTROL, KeyEvent.VK_V);
                timeSleep(1000);
                
                pressKey(KeyEvent.VK_ENTER);
                timeSleep(1000);
                
                pressKey(KeyEvent.VK_DOWN);
                timeSleep(1000);
                
                // Copia o valor na célula/linha atual e, se estiver vazio, reinicia o loop
                hotkey(KeyEvent.VK_CONTROL, KeyEvent.VK_C);
                timeSleep(1000);
                
                String valor = getClipboardText().trim();
                if (valor.isEmpty()) {
                    // nada encontrado nesta linha, volta ao início do while
                    continue;
                }
                
                pressKey(KeyEvent.VK_CONTEXT_MENU); // Tecla Apps
                timeSleep(1000);
                
                for (int i = 0; i < 7; i++) {
                    pressKey(KeyEvent.VK_DOWN);
                }
                
                pressKey(KeyEvent.VK_ENTER);
                timeSleep(1000);
                
                pressKey(KeyEvent.VK_DOWN);
                timeSleep(1000);
                
                pressKey(KeyEvent.VK_ENTER);
                timeSleep(1000);
                
                for (int i = 0; i < 4; i++) {
                    pressKey(KeyEvent.VK_TAB);
                }
                
                pressKey(KeyEvent.VK_ENTER);
                pressKey(KeyEvent.VK_ENTER);
                timeSleep(1000);
                
                hotkey(KeyEvent.VK_ALT, KeyEvent.VK_TAB);
                timeSleep(1000);
                
                pressKey(KeyEvent.VK_RIGHT);
                timeSleep(1000);
                
                pressKey(KeyEvent.VK_SPACE);
                timeSleep(1000);
                
                pressKey(KeyEvent.VK_LEFT);
                timeSleep(2000);
                
                pressKey(KeyEvent.VK_DOWN);
                timeSleep(1000);
                
                if (c == 40) {
                    break;
                }
            }
            
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
    
    // Equivalente ao pyperclip.paste()
    private static String getClipboardText() {
        try {
            Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
            return (String) clipboard.getData(DataFlavor.stringFlavor);
        } catch (Exception e) {
            System.err.println("Erro ao acessar área de transferência: " + e.getMessage());
            return "";
        }
    }
    
    // Equivalente ao pyperclip.copy() (se necessário)
    private static void setClipboardText(String text) {
        StringSelection stringSelection = new StringSelection(text);
        Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
        clipboard.setContents(stringSelection, null);
    }
    
    // Executar apenas se chamado diretamente
    public static void main(String[] args) {
        executarIncluirTurma();
    }
}