package ciencias.numerospseudoaleatorios;

import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class NumerosPseudoaleatorios {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("=== GENERADOR DE NÚMEROS ALEATORIOS UNIFORMES (LCG) ===");
        System.out.print("Ingrese el límite inferior del rango (ej. 0): ");
        int min = scanner.nextInt();

        System.out.print("Ingrese el límite superior del rango (ej. 9): ");
        int max = scanner.nextInt();

        System.out.print("Ingrese la cantidad de veces que debe salir CADA número: ");
        int repeticiones = scanner.nextInt();

        System.out.print("Ingrese una semilla inicial (número entero positivo): ");
        long semilla = scanner.nextLong();

        List<Integer> resultado = generarUniforme(min, max, repeticiones, semilla);

        System.out.println("\n--- Secuencia Generada ---");
        System.out.println(resultado);
        System.out.println("Total de números generados: " + resultado.size());
    }

    /**
     * Genera una secuencia donde cada número en [min, max] aparece exactamente 'repeticiones' veces.
     */
    public static List<Integer> generarUniforme(int min, int max, int repeticiones, long semilla) {
        int m = (max - min) + 1; // Tamaño del rango
        
        // Selección de parámetros a y c según el Teorema de Hull-Dobell
        long a = calcularMultiplicador(m);
        long c = calcularIncremento(m);

        List<Integer> listaFinal = new ArrayList<>();
        long x = Math.abs(semilla) % m; // Ajustar la semilla al rango [0, m-1]

        // Repetimos los ciclos completos N veces para asegurar la distribución idéntica
        for (int r = 0; r < repeticiones; r++) {
            for (int i = 0; i < m; i++) {
                listaFinal.add((int) (x + min));
                x = (a * x + c) % m; // Fórmula LCG
            }
        }

        return listaFinal;
    }

    /**
     * Calcula 'c' coprimo con 'm'.
     */
    private static long calcularIncremento(int m) {
        for (long c = 3; c < m + 10; c += 2) {
            if (gcd(c, m) == 1) {
                return c;
            }
        }
        return 1;
    }

    /**
     * Calcula 'a' tal que (a - 1) cumpla el Teorema de Hull-Dobell para m.
     */
    private static long calcularMultiplicador(int m) {
        List<Integer> factoresPrimos = obtenerFactoresPrimos(m);
        long productoPrimos = 1;
        for (int p : factoresPrimos) {
            productoPrimos *= p;
        }

        long k = productoPrimos;
        if (m % 4 == 0 && k % 4 != 0) {
            k *= 2;
        }

        long a = k + 1;
        // Evitamos un valor trivial de a = 1 si m es primo
        if (a == 2 && m > 2) {
            a += k;
        }
        return a;
    }

    private static long gcd(long a, long b) {
        while (b != 0) {
            long temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    private static List<Integer> obtenerFactoresPrimos(int n) {
        List<Integer> factores = new ArrayList<>();
        int temp = n;
        for (int i = 2; i <= temp; i++) {
            if (temp % i == 0) {
                factores.add(i);
                while (temp % i == 0) {
                    temp /= i;
                }
            }
        }
        return factores;
    }
}