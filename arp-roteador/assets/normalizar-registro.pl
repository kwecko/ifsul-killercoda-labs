#!/usr/bin/perl
# Converte a transcrição de linha de comando em texto legível.
# Não é um emulador completo de aplicações de tela inteira.
use strict;
use warnings;

@ARGV == 1 or die "Uso: normalizar-registro.pl arquivo.log\n";
open my $fh, '<:raw', $ARGV[0] or die "Não foi possível ler o registro: $!\n";
my $texto = '';
defined(read($fh, $texto, 1048577)) or die "Falha ao ler o registro: $!\n";
close $fh;
length($texto) <= 1048576 or die "Registro maior que 1 MiB.\n";
utf8::decode($texto) or die "Registro contém bytes fora de UTF-8; preserve o bruto para consulta.\n";

my @linhas = ('');
my ($linha, $coluna) = (0, 0);
my $largura = 4096;
sub atual {
    $linhas[$linha] //= '';
}
sub escrever {
    my ($valor) = @_;
    atual();
    return if $coluna >= $largura;
    $linhas[$linha] .= ' ' x ($coluna - length($linhas[$linha])) if $coluna > length($linhas[$linha]);
    substr($linhas[$linha], $coluna, 1, $valor);
    $coluna++;
    $linhas[$linha] = substr($linhas[$linha], 0, $largura);
}
sub controle {
    my ($parametros, $comando) = @_;
    return if $parametros =~ /[?<=>:]/; # cores estendidas e modos privados
    my @p = split /;/, $parametros, -1;
    my $n = (@p && $p[0] ne '') ? 0 + $p[0] : 0;
    $n = $largura if $n > $largura;
    my $passos = $n || 1;
    atual();
    if ($comando eq 'C') { $coluna += $passos; }
    elsif ($comando eq 'D') { $coluna -= $passos; }
    elsif ($comando eq 'G' || $comando eq '`') { $coluna = $passos - 1; }
    elsif ($comando eq 'A') { $linha -= $passos; $linha = 0 if $linha < 0; }
    elsif ($comando eq 'B') { $linha += $passos; }
    elsif ($comando eq 'K') {
        if ($n == 0) { substr($linhas[$linha], $coluna) = '' if $coluna < length($linhas[$linha]); }
        elsif ($n == 1) { substr($linhas[$linha], 0, $coluna + 1) = ' ' x ($coluna + 1); }
        elsif ($n == 2) { $linhas[$linha] = ''; }
    }
    elsif ($comando eq 'P') {
        substr($linhas[$linha], $coluna, $passos) = '' if $coluna < length($linhas[$linha]);
    }
    elsif ($comando eq '@' || $comando eq 'X') {
        $linhas[$linha] .= ' ' x ($coluna - length($linhas[$linha])) if $coluna > length($linhas[$linha]);
        substr($linhas[$linha], $coluna, $comando eq '@' ? 0 : $passos) = ' ' x $passos;
        $linhas[$linha] = substr($linhas[$linha], 0, $largura);
    }
    elsif ($comando eq 'J' && ($n == 2 || $n == 3)) {
        # "clear" não deve apagar comandos anteriores na transcrição.
        $linha = scalar(@linhas); $coluna = 0;
    }
    # Ignora cores, modos de colagem, posição absoluta de tela e atributos.
    $coluna = 0 if $coluna < 0;
    $coluna = $largura if $coluna > $largura;
    $linha = 65535 if $linha > 65535;
}

pos($texto) = 0;
while (pos($texto) < length($texto)) {
    if ($texto =~ /\G\e\[([0-?]*)([ -\/]*)([@-~])/gc) {
        controle($1, $3);
    }
    elsif ($texto =~ /\G\e\](?:[^\e\a]|\e(?!\\))*(?:\a|\e\\|\z)/gc) {
        # Título da janela, hyperlinks OSC e metadados do terminal.
    }
    elsif ($texto =~ /\G\e[P^_](?:[^\e]|\e(?!\\))*(?:\e\\|\z)/gc) {
        # Sequências de controle de dispositivos.
    }
    elsif ($texto =~ /\G\e[()][^\n]?/gc || $texto =~ /\G\e[^\n]?/gc) {
        # Outros controles de escape, sem introduzir texto artificial.
    }
    elsif ($texto =~ /\G(.)/gcs) {
        my $c = $1;
        if ($c eq "\n") { $linha++; $coluna = 0; $linha = 65535 if $linha > 65535; }
        elsif ($c eq "\r") { $coluna = 0; }
        elsif ($c eq "\b") { $coluna-- if $coluna > 0; }
        elsif ($c eq "\t") { my $fim = $coluna + 8 - ($coluna % 8); escrever(' ') while $coluna < $fim && $coluna < $largura; }
        elsif (ord($c) >= 32 && ord($c) != 127) { escrever($c); }
    }
}
for (@linhas) { $_ //= ''; s/ +$//; }
pop @linhas while @linhas && $linhas[-1] eq '';
my $saida = join("\n", @linhas) . "\n";
utf8::encode($saida);
length($saida) <= 1048576 or die "Registro legível maior que 1 MiB.\n";
print $saida;
