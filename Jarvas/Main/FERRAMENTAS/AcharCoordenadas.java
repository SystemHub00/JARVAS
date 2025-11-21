package FERRAMENTAS;
import java.awt.MouseInfo;
import java.awt.Point;
import java.awt.Robot;

public class AcharCoordenadas {
    
    public static void main(String[] args) {
        try {
            // Espera 5 segundos (equivalente ao time.sleep(5))
            Thread.sleep(5000);
            
            // Obtém a posição atual do mouse (equivalente ao py.position())
            Point posicao = MouseInfo.getPointerInfo().getLocation();
            int x = (int) posicao.getX();
            int y = (int) posicao.getY();
            
            // Imprime a posição (equivalente ao print)
            System.out.println("Posição atual do mouse: X=" + x + ", Y=" + y);
            
        } catch (InterruptedException e) {
            System.err.println("Thread interrompida: " + e.getMessage());
        }
    }
}